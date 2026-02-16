import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "rag_logs.jsonl"


def log_query(
    query: str,
    answer: str,
    confidence: float,
    latency: float,
    sources: list[str],
):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "confidence": confidence,
        "latency_seconds": latency,
        "num_sources": len(sources),
        "sources": sources,
        "answer_length": len(answer),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
