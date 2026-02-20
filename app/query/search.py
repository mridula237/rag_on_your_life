from typing import List
from langchain_core.documents import Document
from app.indexing.vector_store import get_vector_store


def search_documents(query: str, search_all: bool = False, k: int = 5) -> List[Document]:
    """
    Retrieve relevant documents from vector store.
    """

    vector_store = get_vector_store()

    if search_all:
        results = vector_store.similarity_search(query, k=k)
    else:
        # When not searching across all documents,
        # rely on metadata filtering from frontend logic
        # (you can later extend this with active file tracking if needed)

        results = vector_store.similarity_search(query, k=k)

    return results