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
                    malicious BOOLEAN,
                    semantic_outlier BOOLEAN
            )"""
        )
        cur.close()
        self.conn.commit()

    def insert_log(self, timestamp: str, host: str, message: str,
                   category: str, severity: str, anomaly_score: float,
                   malicious: bool, semantic_outlier: bool) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (timestamp, host, message, category, severity, anomaly_score, malicious, semantic_outlier)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (timestamp, host, message, category, severity, anomaly_score, malicious, semantic_outlier)
        )
        cur.close()
        self.conn.commit()

    def fetch_logs(
        self,
        limit: int = 100,
        page: int | None = None,
        severity: str | None = None,
        host: str | None = None,
        search: str | None = None,
    ) -> Iterable[Tuple[Any, ...]]:
        """Return logs optionally paginated and filtered."""
        query = (
            "SELECT id, timestamp, host, message, category, severity, anomaly_score, malicious, semantic_outlier"
            " FROM logs"
        )
        clauses: list[str] = []
        params: list[Any] = []
        if severity:
            clauses.append("severity = %s")
            params.append(severity)
        if host:
            clauses.append("host = %s")
            params.append(host)
        if search:
            clauses.append("message ILIKE %s")
            params.append(f"%{search}%")
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY id DESC"
        if page is not None:
            offset = (page - 1) * limit
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
        else:
            query += " LIMIT %s"
            params.append(limit)
        cur = self.conn.cursor()
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        return rows

    def get_log_with_context(
        self, log_id: int, context: int = 5
    ) -> list[Tuple[Any, ...]]:
        """Return specified log with preceding context lines."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, host, message FROM logs WHERE id = %s",
            (log_id,),
        )
        main_log = cur.fetchone()
        if not main_log:
            cur.close()
            return []
        cur.execute(
            "SELECT id, timestamp, host, message FROM logs WHERE id < %s ORDER BY id DESC LIMIT %s",
            (log_id, context),
        )
        context_rows = cur.fetchall()[::-1]
        cur.close()
        return context_rows + [main_log]

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
