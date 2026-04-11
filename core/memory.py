import json
from datetime import datetime
from typing import List, Dict, Optional
from db.db import get_commection

Max_History = 20

class Memory:
    """
    Nova's conversation memory.
    Reads and writes to the memory_entries table in nova.db.

    Each message stored as a row with:
        role        : "user" or "assistant"
        content     : message text 
        category    : "general", "task", "reflection", "error",
        importance  : 1 (low) to 5 (high)
        timestamp   : ISO format datetime string
    """

    def__init__(self):
      self,_ensure_table()
      count = self,_count_messages()
      print(f"[Memory] initialized. {count} messages in history.")

    def add(
        self,
        role: str,
        content: str,
        category: str = "general",
        importance: int = 1,

        """
        Add one message to memory.
        