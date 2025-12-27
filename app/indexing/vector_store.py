import os
from langchain_chroma import Chroma
from app.indexing.embeddings import get_embedding_function

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "rag_documents"

def get_vector_store() -> Chroma:
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embedding_function(),
        collection_name=COLLECTION_NAME,
    )
