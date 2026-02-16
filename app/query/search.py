from typing import List, Optional
from langchain_core.documents import Document
from app.indexing.vector_store import get_vector_store


def semantic_search(
    query: str,
    source: Optional[str] = None,
    cross_document: bool = False,
    k: int = 6,
) -> List[Document]:
    store = get_vector_store()

    if cross_document or not source:
        return store.similarity_search(query, k=k)

    return store.similarity_search(
        query,
        k=k,
        filter={"source": source}
    )
