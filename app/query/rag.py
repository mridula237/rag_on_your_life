from typing import List, Tuple
import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.logger import log_query


from app.indexing.vector_store import get_vector_store


# 🔹 LLM configuration
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def retrieve_documents(
    query: str,
    source: str | None,
    cross_document: bool,
):
    """
    Retrieves top-k relevant documents along with similarity scores.
    """
    vector_store = get_vector_store()

    if vector_store is None:
        return []

    if source and not cross_document:
        docs_with_scores = vector_store.similarity_search_with_score(
            query,
            k=5,
            filter={"source": source},
        )
    else:
        docs_with_scores = vector_store.similarity_search_with_score(
            query,
            k=5,
        )

    return docs_with_scores


def answer_with_rag(
    query: str,
    source: str | None = None,
    cross_document: bool = False,
) -> Tuple[str, List[str], float]:

    start_time = time.time()

    docs_with_scores = retrieve_documents(query, source, cross_document)

    if not docs_with_scores:
        return "I don't know.", [], 0.0

    docs = [d[0] for d in docs_with_scores]
    scores = [d[1] for d in docs_with_scores]

    # 🔥 Convert FAISS distance to confidence
    # Lower score = better match in FAISS (L2 distance)
    # We invert it for easier interpretation
    avg_distance = sum(scores) / len(scores)
    confidence = round(1 / (1 + avg_distance), 3)

    # 🔥 Threshold
    if confidence < 0.2:
        return "I don't know.", [], confidence

    context = "\n\n".join(d.page_content for d in docs)

    messages = [
        SystemMessage(
            content=(
                "You are a document reasoning assistant. "
                "Answer ONLY using the provided context. "
                "If the answer is not explicitly supported by the context, respond with 'I don't know.'"
            )
        ),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion:\n{query}"
        ),
    ]

    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)

    latency = round(time.time() - start_time, 3)

    print(f"RAG latency: {latency}s | Confidence: {confidence}")

    log_query(
        query=query,
        answer=answer,
        confidence=confidence,
        latency=latency,
        sources=sources,
)


    sources = sorted({
        f"{d.metadata.get('source', 'unknown')} – page {d.metadata.get('page', '?')}"
        for d in docs
    })

    return answer, sources, confidence
