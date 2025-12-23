from typing import List
import pdfplumber
import pytesseract
from PIL import Image

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.indexing.vector_store import get_vector_store


def ingest_file(path: str, original_name: str) -> int:
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
            else:
                # OCR fallback
                image = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(image)
                if ocr_text:
                    text += ocr_text + "\n"

    if not text.strip():
        raise ValueError("No text could be extracted even after OCR.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    chunks = splitter.split_text(text)

    docs: List[Document] = [
        Document(
            page_content=chunk,
            metadata={"source": original_name, "chunk": i},
        )
        for i, chunk in enumerate(chunks)
    ]

    vs = get_vector_store()
    vs.add_documents(docs)

    return len(docs)
