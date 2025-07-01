import re
from collections import defaultdict
from typing import Iterable, Dict

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
