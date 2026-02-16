from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.indexing.vector_store import get_vector_store

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_upload(file_bytes: bytes, filename: str) -> Path:
    path = UPLOAD_DIR / filename
    path.write_bytes(file_bytes)
    return path


def ingest_pdf(path: Path, source_name: str) -> int:
    loader = PyPDFLoader(str(path))
    documents = loader.load()

    for doc in documents:
        doc.metadata["source"] = source_name

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    vectorstore = get_vector_store()
    vectorstore.add_documents(chunks)
    vectorstore.save_local("vector_store")

    return len(chunks)
