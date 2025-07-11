CREATE TABLE logs (
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
);

CREATE TABLE log_analysis (
    id SERIAL PRIMARY KEY,
    log_id INTEGER REFERENCES logs(id),
    analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analyzed_logs (
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
);

CREATE TABLE network_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event TEXT,
    source TEXT,
    label TEXT,
    score REAL
);

CREATE TABLE network_analysis (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES network_events(id),
    analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analyzed_network_events (
    id SERIAL PRIMARY KEY,
    event_id INTEGER UNIQUE REFERENCES network_events(id),
    timestamp TIMESTAMP,
    event TEXT,
    label TEXT,
    score REAL,
    source TEXT,
    analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
