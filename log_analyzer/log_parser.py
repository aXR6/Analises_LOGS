import re
from datetime import datetime
from typing import Tuple

CATEGORY_PATTERNS = {
    'ERROR': re.compile(r'error|failed', re.IGNORECASE),
    'WARNING': re.compile(r'warning|deprecated', re.IGNORECASE),
    'CRITICAL': re.compile(r'critical', re.IGNORECASE),
    'MALICIOUS': re.compile(r'denied|attack|malware|unauthorized', re.IGNORECASE),
}

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


def parse_log_line(line: str) -> Tuple[str, str, str, str, bool]:
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

    category = 'INFO'
    malicious = False
    for cat, regex in CATEGORY_PATTERNS.items():
        if regex.search(msg):
            category = cat
            if cat == 'MALICIOUS':
                malicious = True
            break

    return ts, host, msg, category, malicious
