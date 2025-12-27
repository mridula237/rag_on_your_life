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

    context_blocks: List[str] = [d.page_content for d in docs if d.page_content]
    context = "\n\n---\n\n".join(context_blocks)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in .env")

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.2)

    prompt = f"""
You are a helpful RAG assistant.
Use ONLY the provided context to answer.
If the answer is not in the context, say "I don't know."

Question:
{query}

Context:
{context}

Answer:
""".strip()

    resp = llm.invoke(prompt)
    answer = resp.content if hasattr(resp, "content") else str(resp)

    sources = []
    seen = set()
    for d in docs:
        src = d.metadata.get("source")
        page = d.metadata.get("page")
        key = (src, page)
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "source": src,
            "page": page,
            "chunk": d.metadata.get("chunk"),
        })

    return {"answer": answer, "sources": sources}
