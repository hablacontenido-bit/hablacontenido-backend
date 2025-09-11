# app/memory.py
import os, json
from collections import defaultdict
from threading import Lock

class Memory:
    def __init__(self, filename="memory.json"):
        self.filename = os.path.join(os.path.dirname(__file__), filename)
        self.histories = defaultdict(list)
        self.lock = Lock()
        self._load()

    def _load(self):
        """Load memory from disk if available"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.histories.update(data)
            except Exception:
                self.histories = defaultdict(list)

    def _save(self):
        """Save memory to disk"""
        with self.lock:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.histories, f, indent=2, ensure_ascii=False)

    def get_history(self, user_id: str):
        return self.histories[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        self.histories[user_id].append({"role": role, "content": content})
        self._save()

    def clear_history(self, user_id: str):
        self.histories[user_id] = []
        self._save()
