from app.indexing.vector_store import get_vector_store

def semantic_search(query: str, top_k: int = 5):
    vs = get_vector_store()
    return vs.similarity_search(query, k=top_k)
