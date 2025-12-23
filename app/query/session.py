# app/query/session.py

from typing import List, Dict

class RAGSession:
    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self):
        return self.history
