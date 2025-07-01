CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    host TEXT,
    message TEXT,
    category TEXT,
    severity TEXT,
    anomaly_score REAL,
    malicious BOOLEAN,
    semantic_outlier BOOLEAN
);
