from typing import List
from langchain_core.documents import Document
from app.indexing.vector_store import get_vector_store


def semantic_search(query: str, top_k: int = 5) -> List[Document]:
    store = get_vector_store()
    return store.similarity_search(query, k=top_k)
