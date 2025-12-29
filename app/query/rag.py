import os
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.query.search import semantic_search

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def answer_with_rag(query: str, top_k: int = 5) -> Dict[str, Any]:
    docs = semantic_search(query, top_k=top_k)

    if not docs:
        return {"answer": "I don't know.", "sources": []}

    context = "\n\n---\n\n".join(
        d.page_content for d in docs if d.page_content
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "answer": "OPENAI_API_KEY is missing.",
            "sources": [],
        }

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0.2,
    )

    prompt = f"""
You are a helpful RAG assistant.
Use ONLY the provided context.
If the answer is not in the context, say "I don't know."

Question:
{query}

Context:
{context}

Answer:
""".strip()

    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    seen = set()
    sources = []
    for d in docs:
        key = (d.metadata.get("source"), d.metadata.get("page"))
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "chunk": d.metadata.get("chunk"),
        })

    return {"answer": answer, "sources": sources}
