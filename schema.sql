CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    host TEXT,
    message TEXT,
    category TEXT,
    severity TEXT,
    anomaly_score REAL,
    malicious INTEGER
);
