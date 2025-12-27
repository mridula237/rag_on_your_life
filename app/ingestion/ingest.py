import os
from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.indexing.vector_store import get_vector_store

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Optional OCR (only works if installed)
OCR_AVAILABLE = False
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


def save_upload(file_bytes: bytes, filename: str) -> str:
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)


def _extract_text_normal(pdf_path: Path) -> List[tuple[int, str]]:
    """Return list of (page_number_1_based, text)."""
    reader = PdfReader(str(pdf_path))
    out: List[tuple[int, str]] = []

    for i, page in enumerate(reader.pages):
        text: Optional[str] = None
        try:
            text = page.extract_text()
        except Exception:
            text = None

        if text:
            text = text.strip()
            if text:
                out.append((i + 1, text))

    return out


def _extract_text_ocr(pdf_path: Path) -> List[tuple[int, str]]:
    """OCR fallback for scanned PDFs. Requires pdf2image + pytesseract + poppler + tesseract."""
    if not OCR_AVAILABLE:
        return []

    images = convert_from_path(str(pdf_path))
    out: List[tuple[int, str]] = []

    for i, img in enumerate(images):
        txt = pytesseract.image_to_string(img) or ""
        txt = txt.strip()
        if txt:
            out.append((i + 1, txt))

    return out


def ingest_pdf(pdf_path: str, source_name: str) -> int:
    pdf_path = Path(pdf_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs: List[Document] = []

    pages = _extract_text_normal(pdf_path)

    # If no text, try OCR
    if not pages:
        pages = _extract_text_ocr(pdf_path)

    if not pages:
        raise ValueError(
            "No readable text found in this PDF. "
            "If this is a scanned PDF, install OCR dependencies (pdf2image + pytesseract + poppler + tesseract)."
        )

    for page_num, text in pages:
        chunks = splitter.split_text(text)
        for chunk_idx, chunk in enumerate(chunks):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": source_name,
                        "page": page_num,
                        "chunk": chunk_idx,
                    },
                )
            )

    vs = get_vector_store()

    # ✅ Re-upload same filename: remove old vectors for this file first
    try:
        vs._collection.delete(where={"source": source_name})
    except Exception:
        pass

    vs.add_documents(docs)
    return len(docs)
