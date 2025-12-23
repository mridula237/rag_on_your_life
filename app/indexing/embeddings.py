import os
from langchain_openai import OpenAIEmbeddings

def get_embedding_function():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
    )
