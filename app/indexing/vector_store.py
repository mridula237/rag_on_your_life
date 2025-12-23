from langchain_chroma import Chroma
from app.indexing.embeddings import get_embedding_function
import os

CHROMA_DIR = "./chroma_db"

def get_vector_store():
    os.makedirs(CHROMA_DIR, exist_ok=True)

    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embedding_function(),
        collection_name="rag_documents",
    )
