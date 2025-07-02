import time
from pathlib import Path
from log_analyzer.log_db import LogDB
from log_analyzer.log_parser import parse_log_line
from log_analyzer.config import LOG_FILE
from log_analyzer.semantic_anomaly import OnlineSemanticDetector


def follow(file_path: Path):
    file_path.touch(exist_ok=True)
    with file_path.open('r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

def alert(msg: str) -> None:
    print(f"ALERT: {msg}")


def main():
    db = LogDB()
    semantic = OnlineSemanticDetector()
    for line in follow(LOG_FILE):
        ts, host, program, msg, severity, anomaly_score, malicious = parse_log_line(line)
        semantic_outlier = semantic.add(msg)
        db.insert_log(
            ts,
            host,
            program,
            msg,
            severity,
            severity,
            anomaly_score,
            malicious,
            semantic_outlier,
        )
        if malicious or semantic_outlier:
            alert(msg)


if __name__ == '__main__':
    main()
