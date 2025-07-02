import re
from collections import defaultdict
from typing import Iterable, Dict, Tuple, Optional

ATTACK_PATTERNS = {
    'ssh-brute-force': re.compile(r'Failed password|invalid user', re.IGNORECASE),
    'unauthorized-access': re.compile(r'denied|unauthorized', re.IGNORECASE),
    'malware': re.compile(r'malware', re.IGNORECASE),
    'attack': re.compile(r'attack', re.IGNORECASE),
}


def classify_attack(message: str) -> str | None:
    for name, pattern in ATTACK_PATTERNS.items():
        if pattern.search(message):
            return name
    return None


def count_attack_types(messages: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for msg in messages:
        atype = classify_attack(msg)
        if atype:
            counts[atype] += 1
    return counts


IP_RE = re.compile(r'(?:\d{1,3}\.){3}\d{1,3}')


def extract_ips(message: str) -> Tuple[Optional[str], Optional[str]]:
    """Return source and destination IPs if present in the log message."""
    ips = IP_RE.findall(message)
    src = ips[0] if ips else None
    dst = ips[1] if len(ips) > 1 else None
    return src, dst
