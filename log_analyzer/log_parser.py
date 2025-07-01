import re
from datetime import datetime
from typing import Tuple
from functools import lru_cache
from transformers import pipeline
from log_analyzer.config import SEVERITY_MODEL, ANOMALY_MODEL, ANOMALY_THRESHOLD

MALICIOUS_RE = re.compile(r'denied|attack|malware|unauthorized', re.IGNORECASE)

MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

SYSLOG_RE = re.compile(
    r'^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<msg>.*)$'
)

# Formato ISO 8601 utilizado quando a configuracao recomendada em
# docs/rsyslog_optimization.md esta habilitada.
ISO_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))\s+(?P<host>\S+)\s+(?P<msg>.*)$'
)


@lru_cache(maxsize=1)
def _severity_classifier():
    """Lazy load classifier for severity levels."""
    return pipeline("text-classification", model=SEVERITY_MODEL)


@lru_cache(maxsize=1)
def _anomaly_detector():
    """Lazy load anomaly detection model."""
    return pipeline("text-classification", model=ANOMALY_MODEL)


def parse_log_line(line: str) -> Tuple[str, str, str, str, float, bool]:
    match = SYSLOG_RE.match(line)
    if match:
        month = MONTHS.get(match.group('month'), 1)
        day = int(match.group('day'))
        time_part = match.group('time')
        year = datetime.utcnow().year
        ts = datetime(year, month, day, *map(int, time_part.split(':'))).isoformat()
        host = match.group('host')
        msg = match.group('msg')
    else:
        iso_match = ISO_RE.match(line)
        if iso_match:
            ts = iso_match.group('ts')
            # converte para ISO padronizado
            ts = datetime.fromisoformat(ts.replace('Z', '+00:00')).isoformat()
            host = iso_match.group('host')
            msg = iso_match.group('msg')
        else:
            ts = datetime.utcnow().isoformat()
            host = 'unknown'
            msg = line.strip()

    # Detection using LLM models
    sev_res = _severity_classifier()(msg)[0]
    severity = sev_res['label']

    anomaly_res = _anomaly_detector()(msg)[0]
    # LABEL_0 usually represents normal lines in the available model
    anomaly_score = (
        anomaly_res['score']
        if anomaly_res['label'] != 'LABEL_0'
        else 1 - anomaly_res['score']
    )

    malicious = bool(MALICIOUS_RE.search(msg)) or anomaly_score >= ANOMALY_THRESHOLD

    return ts, host, msg, severity, anomaly_score, malicious
