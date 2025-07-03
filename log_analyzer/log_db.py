import psycopg2
from typing import Iterable, Tuple, Any
from datetime import datetime

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
                    graylog_id TEXT,
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
            "ALTER TABLE logs ADD COLUMN IF NOT EXISTS graylog_id TEXT"
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
                    graylog_id TEXT,
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
            "ALTER TABLE analyzed_logs ADD COLUMN IF NOT EXISTS graylog_id TEXT"
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS network_events (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event TEXT,
                    source TEXT,
                    label TEXT,
                    score REAL
            )"""
        )
        cur.execute(
            "ALTER TABLE network_events ADD COLUMN IF NOT EXISTS source TEXT"
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS network_analysis (
                    id SERIAL PRIMARY KEY,
                    event_id INTEGER REFERENCES network_events(id),
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS analyzed_network_events (
                    id SERIAL PRIMARY KEY,
                    event_id INTEGER UNIQUE REFERENCES network_events(id),
                    timestamp TIMESTAMP,
                    event TEXT,
                    label TEXT,
                    score REAL,
                    source TEXT,
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        cur.close()
        self.conn.commit()

    def insert_log(
        self,
        timestamp: str,
        host: str,
        program: str,
        message: str,
        category: str,
        severity: str,
        anomaly_score: float,
        malicious: bool,
        semantic_outlier: bool,
        graylog_id: str | None = None,
    ) -> int:
        """Insert log and return its ID. Also index in Elasticsearch if available."""
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (graylog_id, timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                graylog_id,
                timestamp,
                host,
                program,
                message,
                category,
                severity,
                anomaly_score,
                malicious,
                semantic_outlier,
            ),
        )
        log_id = cur.fetchone()[0]
        cur.close()
        self.conn.commit()

        try:
            from .es_client import index_log

            index_log(
                log_id,
                {
                    "timestamp": timestamp,
                    "host": host,
                    "program": program,
                    "message": message,
                    "category": category,
                    "severity": severity,
                    "anomaly_score": anomaly_score,
                    "malicious": malicious,
                    "semantic_outlier": semantic_outlier,
                },
            )
        except Exception:
            pass

        try:
            from .graylog_client import send_gelf

            gelf = {
                "version": "1.1",
                "host": host,
                "short_message": message,
                "timestamp": datetime.fromisoformat(timestamp).timestamp(),
                "_program": program,
                "_category": category,
                "_severity": severity,
                "_anomaly_score": anomaly_score,
                "_malicious": malicious,
                "_semantic_outlier": semantic_outlier,
            }
            send_gelf(gelf)
        except Exception:
            pass

        return log_id

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
            "SELECT id, graylog_id, timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier"
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
            from .es_client import search_logs

            ids = search_logs(search, limit=limit, page=page or 1)
            if not ids:
                return []
            clauses.append("id = ANY(%s)")
            params.append(ids)
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
            "SELECT id, graylog_id, timestamp, host, program, message, category, severity, anomaly_score, malicious, semantic_outlier FROM logs WHERE id = %s",
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
            "SELECT id, graylog_id, timestamp, host, message FROM logs WHERE id = %s",
            (log_id,),
        )
        main_log = cur.fetchone()
        if not main_log:
            cur.close()
            return []
        cur.execute(
            "SELECT id, graylog_id, timestamp, host, message FROM logs WHERE id < %s ORDER BY id DESC LIMIT %s",
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

    def fetch_recent_attack_logs(self, limit: int = 5) -> Iterable[Tuple[Any, ...]]:
        """Return recent malicious log entries with all fields."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT timestamp, host, message FROM logs WHERE malicious = TRUE ORDER BY id DESC LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
        cur.close()
        return rows

    def insert_network_event(
        self, event: str, label: str, score: float, source: str | None = None
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO network_events (event, label, score, source) VALUES (%s, %s, %s, %s) RETURNING id",
            (event, label, score, source),
        )
        event_id = cur.fetchone()[0]
        cur.close()
        self.conn.commit()

        try:
            from .graylog_client import send_gelf

            gelf = {
                "version": "1.1",
                "host": source or "network",
                "short_message": event,
                "timestamp": datetime.utcnow().timestamp(),
                "_label": label,
                "_score": score,
                "_source": source,
            }
            send_gelf(gelf)
        except Exception:
            pass

        return event_id

    def fetch_network_events(
        self,
        limit: int = 100,
        page: int | None = None,
        source: str | None = None,
    ) -> Iterable[Tuple[Any, ...]]:
        query = "SELECT id, timestamp, event, label, score, source FROM network_events"
        clauses: list[str] = []
        params: list[Any] = []
        if source:
            clauses.append("source = %s")
            params.append(source)
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

    def fetch_network_event(self, event_id: int) -> tuple[Any, ...] | None:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, event, label, score, source FROM network_events WHERE id = %s",
            (event_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row

    def insert_network_analysis(self, event_id: int, analysis: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO network_analysis (event_id, analysis) VALUES (%s, %s)",
            (event_id, analysis),
        )
        cur.close()
        self.conn.commit()

    def insert_analyzed_network_event(self, event_id: int, analysis: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT timestamp, event, label, score, source FROM network_events WHERE id = %s",
            (event_id,),
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return
        cur.execute(
            """
            INSERT INTO analyzed_network_events (event_id, timestamp, event, label, score, source, analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO UPDATE SET analysis = EXCLUDED.analysis,
                created_at = CURRENT_TIMESTAMP
            """,
            (event_id, *row, analysis),
        )
        cur.close()
        self.conn.commit()

    def fetch_analyzed_network_events(
        self, limit: int = 100, page: int | None = None
    ) -> Iterable[Tuple[Any, ...]]:
        query = (
            "SELECT event_id, timestamp, event, label, score, source, analysis, created_at"
            " FROM analyzed_network_events ORDER BY created_at DESC"
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

    def count_analyzed_network_events(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM analyzed_network_events")
        count = cur.fetchone()[0]
        cur.close()
        return count

    def list_network_sources(self) -> Iterable[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT source FROM network_events WHERE source IS NOT NULL")
        rows = [r[0] for r in cur.fetchall()]
        cur.close()
        return rows

    def count_logs(self) -> int:
        """Return total number of log entries."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM logs")
        count = cur.fetchone()[0]
        cur.close()
        return count

    def count_analyzed_logs(self) -> int:
        """Return number of analyzed log entries."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM analyzed_logs")
        count = cur.fetchone()[0]
        cur.close()
        return count

    def count_network_events(self) -> int:
        """Return total number of network events."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM network_events")
        count = cur.fetchone()[0]
        cur.close()
        return count

    def count_network_by_label(self) -> Iterable[Tuple[str, int]]:
        """Return number of network events grouped by label."""
        cur = self.conn.cursor()
        cur.execute("SELECT label, COUNT(*) FROM network_events GROUP BY label")
        rows = cur.fetchall()
        cur.close()
        return rows

    def close(self) -> None:
        self.conn.close()
