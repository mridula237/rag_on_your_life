from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from app.indexing.vector_store import get_vector_store, persist_vector_store

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def save_upload(file_bytes: bytes, filename: str) -> Path:
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def ingest_pdf(file_path: str, filename: str) -> int:
    """
    Ingest a PDF file, attach metadata, and store embeddings.
    """

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    if not docs:
        return 0

    # 🔥 Attach clean metadata for filtering later
    for doc in docs:
        doc.metadata["source"] = filename

    vector_store = get_vector_store()
    vector_store.add_documents(docs)

    persist_vector_store(vector_store)

    return len(docs)