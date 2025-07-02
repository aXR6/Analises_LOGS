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
                    program TEXT,
                    message TEXT,
                    category TEXT,
                    severity TEXT,
                    anomaly_score REAL,
                    malicious BOOLEAN,
                    semantic_outlier BOOLEAN
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS log_analysis (
                    id SERIAL PRIMARY KEY,
                    log_id INTEGER REFERENCES logs(id),
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS analyzed_logs (
                    id SERIAL PRIMARY KEY,
                    log_id INTEGER UNIQUE REFERENCES logs(id),
                    timestamp TIMESTAMP,
                    host TEXT,
                    program TEXT,
                    message TEXT,
                    category TEXT,
                    severity TEXT,
                    anomaly_score REAL,
                    malicious BOOLEAN,
                    semantic_outlier BOOLEAN,
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS network_events (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event TEXT,
                    label TEXT,
                    score REAL
            )"""
        )
        cur.close()
        self.conn.commit()

    def insert_log(self, timestamp: str, host: str, program: str, message: str,
                   category: str, severity: str, anomaly_score: float,
                   malicious: bool, semantic_outlier: bool) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier)
        )
        cur.close()
        self.conn.commit()

    def fetch_logs(
        self,
        limit: int = 100,
        page: int | None = None,
        severity: str | None = None,
        host: str | None = None,
        program: str | None = None,
        search: str | None = None,
    ) -> Iterable[Tuple[Any, ...]]:
        """Return logs optionally paginated and filtered."""
        query = (
            "SELECT id, timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier"
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
        if program:
            clauses.append("program = %s")
            params.append(program)
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

    def fetch_log(self, log_id: int) -> tuple[Any, ...] | None:
        """Return a single log entry by ID with all fields."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier FROM logs WHERE id = %s",
            (log_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row

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

    def count_by_severity(self) -> Iterable[Tuple[str, int]]:
        """Return number of logs grouped by severity."""
        cur = self.conn.cursor()
        cur.execute("SELECT severity, COUNT(*) FROM logs GROUP BY severity")
        rows = cur.fetchall()
        cur.close()
        return rows

    def insert_analysis(self, log_id: int, analysis: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO log_analysis (log_id, analysis) VALUES (%s, %s)",
            (log_id, analysis),
        )
        cur.close()
        self.conn.commit()

    def insert_analyzed_log(self, log_id: int, analysis: str) -> None:
        """Copy log to analyzed_logs table along with the analysis result."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier "
            "FROM logs WHERE id = %s",
            (log_id,),
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return
        cur.execute(
            """
            INSERT INTO analyzed_logs (log_id, timestamp, host, program, message, category, severity,
                                      anomaly_score, malicious, semantic_outlier, analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (log_id) DO UPDATE SET analysis = EXCLUDED.analysis,
                created_at = CURRENT_TIMESTAMP
            """,
            (log_id, *row, analysis),
        )
        cur.close()
        self.conn.commit()

    def fetch_analysis(self, log_id: int) -> Iterable[Tuple[Any, ...]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, analysis, created_at FROM log_analysis WHERE log_id = %s ORDER BY id DESC",
            (log_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return rows

    def fetch_analyzed_logs(
        self, limit: int = 100, page: int | None = None
    ) -> Iterable[Tuple[Any, ...]]:
        """Return logs that have been analyzed by the LLM."""
        query = (
            "SELECT log_id, timestamp, host, program, message, category, severity,"
            " anomaly_score, malicious, semantic_outlier, analysis, created_at"
            " FROM analyzed_logs ORDER BY created_at DESC"
        )
        params: list[Any] = []
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

    def fetch_recent_malicious(self, limit: int = 100) -> Iterable[str]:
        """Return messages flagged as malicious."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT message FROM logs WHERE malicious = TRUE ORDER BY id DESC LIMIT %s",
            (limit,),
        )
        rows = [r[0] for r in cur.fetchall()]
        cur.close()
        return rows

    def insert_network_event(self, event: str, label: str, score: float) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO network_events (event, label, score) VALUES (%s, %s, %s)",
            (event, label, score),
        )
        cur.close()
        self.conn.commit()

    def fetch_network_events(self, limit: int = 100, page: int | None = None) -> Iterable[Tuple[Any, ...]]:
        query = "SELECT id, timestamp, event, label, score FROM network_events ORDER BY id DESC"
        params: list[Any] = []
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

    def close(self) -> None:
        self.conn.close()
