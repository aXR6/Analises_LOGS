import sqlite3
from pathlib import Path
from typing import Iterable, Tuple, Any

from .config import LOG_DB_PATH

class LogDB:
    def __init__(self, db_path: Path = LOG_DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    host TEXT,
                    message TEXT,
                    category TEXT,
                    severity TEXT,
                    anomaly_score REAL,
                    malicious INTEGER
            )"""
        )
        # ensure new columns exist when migrating from older versions
        cur.execute("PRAGMA table_info(logs)")
        cols = [row[1] for row in cur.fetchall()]
        if 'severity' not in cols:
            cur.execute("ALTER TABLE logs ADD COLUMN severity TEXT")
        if 'anomaly_score' not in cols:
            cur.execute("ALTER TABLE logs ADD COLUMN anomaly_score REAL")
        self.conn.commit()

    def insert_log(self, timestamp: str, host: str, message: str,
                   category: str, severity: str, anomaly_score: float,
                   malicious: bool) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (timestamp, host, message, category, severity, anomaly_score, malicious)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, host, message, category, severity, anomaly_score, int(malicious))
        )
        self.conn.commit()

    def fetch_logs(self, limit: int = 100) -> Iterable[Tuple[Any, ...]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, host, message, category, severity, anomaly_score, malicious"
            " FROM logs ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cur.fetchall()

    def count_by_category(self) -> Iterable[Tuple[str, int]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT category, COUNT(*) FROM logs GROUP BY category"
        )
        return cur.fetchall()

    def close(self) -> None:
        self.conn.close()
