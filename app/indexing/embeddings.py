import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import OpenAIEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def get_embedding_function():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in .env")

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )
