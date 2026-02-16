from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_DIR = Path("vector_store")
VECTOR_DIR.mkdir(exist_ok=True)

_embeddings = None
_vectorstore = None


def get_vector_store():
    global _embeddings, _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    _embeddings = OpenAIEmbeddings()

    if (VECTOR_DIR / "index.faiss").exists():
        _vectorstore = FAISS.load_local(
            VECTOR_DIR,
            _embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        _vectorstore = FAISS.from_texts([], _embeddings)
        _vectorstore.save_local(VECTOR_DIR)

    return _vectorstore
