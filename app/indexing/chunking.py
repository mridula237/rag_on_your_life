def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Returns:
      [{"chunk_index": 0, "text": "..."}, {"chunk_index": 1, "text": "..."}]
    Chunking is word-based (simple + reliable).
    """
    words = text.split()
    chunks = []

    start = 0
    idx = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append({"chunk_index": idx, "text": chunk})
            idx += 1
        start += max(1, chunk_size - overlap)

    return chunks
