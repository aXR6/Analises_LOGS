import psycopg2
from typing import Iterable, Tuple, Any

from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class LogDB:
    def __init__(self):
        user = DB_USER
        password = DB_PASSWORD

        self.conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=user,
            password=password,
        )
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    host TEXT,
                    message TEXT,
                    category TEXT,
                    severity TEXT,
                    anomaly_score REAL,
                    malicious BOOLEAN
            )"""
        )
        cur.close()
        self.conn.commit()

    def insert_log(self, timestamp: str, host: str, message: str,
                   category: str, severity: str, anomaly_score: float,
                   malicious: bool) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (timestamp, host, message, category, severity, anomaly_score, malicious)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (timestamp, host, message, category, severity, anomaly_score, malicious)
        )
        cur.close()
        self.conn.commit()

    def fetch_logs(self, limit: int = 100) -> Iterable[Tuple[Any, ...]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, host, message, category, severity, anomaly_score, malicious"
            " FROM logs ORDER BY id DESC LIMIT %s",
            (limit,)
        )
        rows = cur.fetchall()
        cur.close()
        return rows

    def count_by_category(self) -> Iterable[Tuple[str, int]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT category, COUNT(*) FROM logs GROUP BY category"
        )
        rows = cur.fetchall()
        cur.close()
        return rows

    def close(self) -> None:
        self.conn.close()
