import sqlite3
from pathlib import Path
from typing import List, Tuple


class WriteQueue:
    """Simple SQLite-backed queue for voucher data."""

    def __init__(self, db_path: str = "queue.db") -> None:
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def enqueue(self, payload: str, data_type: str = "xml") -> int:
        """Add a new item to the queue."""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO queue (payload, data_type, status) VALUES (?, ?, 'pending')",
                (payload, data_type),
            )
            return cur.lastrowid

    def get_pending(self) -> List[Tuple[int, str, str]]:
        cur = self.conn.execute(
            "SELECT id, payload, data_type FROM queue WHERE status='pending' ORDER BY id"
        )
        return cur.fetchall()

    def mark_complete(self, task_id: int) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE queue SET status='complete' WHERE id=?",
                (task_id,),
            )

    def close(self) -> None:
        self.conn.close()
