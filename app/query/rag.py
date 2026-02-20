import os
import json
from dotenv import load_dotenv
from typing import Optional
import numpy as np

from langchain_openai import ChatOpenAI
from app.indexing.vector_store import get_vector_store

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True
)


# --------------------------------------------------
# SSE helper
# --------------------------------------------------
def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# --------------------------------------------------
# Retrieve documents
# --------------------------------------------------
def retrieve_documents(query: str, selected_file: Optional[str], search_all: bool, k: int = 6):
    vector_store = get_vector_store()

    if vector_store is None:
        return [], [], 0.0

    docs_with_scores = vector_store.similarity_search_with_score(query, k=k)

    filtered_docs = []
    scores = []

    for doc, score in docs_with_scores:
        source_file = doc.metadata.get("source", "unknown")

        if not search_all and selected_file:
            if source_file != selected_file:
                continue

        filtered_docs.append(doc)
        scores.append(float(score))

    if scores:
        avg_score = float(np.mean(scores))
        confidence = round(1 / (1 + avg_score), 3)
    else:
        confidence = 0.0

    return filtered_docs, confidence


# --------------------------------------------------
# Streaming Answer
# --------------------------------------------------
def answer_with_rag_stream(query: str, selected_file=None, search_all=False):

    try:
        docs, confidence = retrieve_documents(query, selected_file, search_all)

        if not docs:
            yield sse("error", {"message": "No relevant documents found."})
            return

        context = "\n\n".join([doc.page_content for doc in docs])

        yield sse("thinking", {"status": "Analyzing documents..."})

        prompt = f"""
You are a helpful AI assistant.

Answer using ONLY the context below.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{query}
"""

        response = llm.stream(prompt)

        for chunk in response:
            if chunk.content:
                yield sse("token", {"token": chunk.content})

        # Send sources cleanly
        yield sse("sources", {
            "sources": [
                f"{doc.metadata.get('source', 'unknown')} — page {doc.metadata.get('page', '?')}"
                for doc in docs
            ]
        })

        yield sse("done", {"confidence": confidence})

    except Exception as e:
        yield sse("error", {"message": str(e)})