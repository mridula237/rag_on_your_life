from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a document classifier.
Classify the document into one of:
- lecture_notes
- research_paper
- receipt
- email
- screenshot
- other

Return ONLY the label.
"""

def classify_document(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:3000]}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()
