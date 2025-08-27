# app/memory.py
from collections import defaultdict

class Memory:
    def __init__(self):
        self.histories = defaultdict(list)

    def get_history(self, user_id: str):
        return self.histories[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        self.histories[user_id].append({"role": role, "content": content})

    def clear_history(self, user_id: str):
        self.histories[user_id] = []
