import time
from pathlib import Path
from transformers import pipeline

from log_analyzer.log_db import LogDB
from log_analyzer.config import (
    NIDS_MODEL,
    NET_LOG_FILE,
    DEVICE_TYPE,
    NIDS_TOKENIZER,
)


def follow(path: Path):
    path.touch(exist_ok=True)
    with path.open('r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line.strip()


def main():
    device = 0 if DEVICE_TYPE.lower() == "cuda" else -1
    tokenizer = NIDS_TOKENIZER or NIDS_MODEL
    clf = pipeline(
        "text-classification",
        model=NIDS_MODEL,
        tokenizer=tokenizer,
        device=device,
    )
    db = LogDB()
    module = "network_nids"
    try:
        for line in follow(NET_LOG_FILE):
            result = clf(line)[0]
            label = result.get("label", "")
            score = float(result.get("score", 0.0))
            db.insert_network_event(line, label, score, module)
            if label.lower() != "normal":
                print(f"ALERTA NIDS: {label} - {line}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
