from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

CHROMA_DIR.mkdir(exist_ok=True)


def get_vector_store():
    embeddings = OpenAIEmbeddings()

    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings
    )


def persist_vector_store(vector_store):
    vector_store.persist()