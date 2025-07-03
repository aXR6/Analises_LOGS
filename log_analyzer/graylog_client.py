import json
from typing import Any, Mapping

import requests

from log_analyzer.config import GRAYLOG_URL


def send_gelf(payload: Mapping[str, Any]) -> None:
    """Send a GELF payload to Graylog if GRAYLOG_URL is defined."""
    if not GRAYLOG_URL:
        return

    try:
        headers = {"Content-Type": "application/json"}
        # requests will raise for non-2xx responses
        requests.post(GRAYLOG_URL, data=json.dumps(payload), headers=headers, timeout=5).raise_for_status()
    except Exception:
        # Ignore failures to avoid breaking the collector
        pass
