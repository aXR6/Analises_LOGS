import time
from pathlib import Path
from log_analyzer.log_db import LogDB
from log_analyzer.log_parser import parse_log_line
from log_analyzer.config import LOG_FILE


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
    for line in follow(LOG_FILE):
        ts, host, msg, severity, anomaly_score, malicious = parse_log_line(line)
        db.insert_log(ts, host, msg, severity, severity, anomaly_score, malicious)
        if malicious:
            alert(msg)


if __name__ == '__main__':
    main()
