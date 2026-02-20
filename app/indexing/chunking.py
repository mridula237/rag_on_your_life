from __future__ import annotations
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_documents(
    docs: List[Document],
    chunk_size: int = 900,
    overlap: int = 150,
) -> List[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks: List[Document] = []

    for d in docs:
        split_docs = splitter.split_documents([d])
        for c in split_docs:
            c.metadata = dict(d.metadata or {}) | dict(c.metadata or {})
            chunks.append(c)

    return chunks
