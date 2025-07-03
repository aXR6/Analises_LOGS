#!/usr/bin/env python3
"""Start log collector, network sniffer and NIDS on container startup."""

import os
import signal
import subprocess
import sys

processes = []

MODULES = [
    "log_analyzer.net_sniffer",
    "log_analyzer.collector",
    "log_analyzer.network_nids",
]


def start() -> None:
    """Start all required modules as subprocesses."""
    interface = os.getenv("NET_INTERFACE")
    if not interface:
        print("Variavel NET_INTERFACE nao definida.")
        sys.exit(1)
    for module in MODULES:
        proc = subprocess.Popen([sys.executable, "-m", module])
        processes.append(proc)


def stop(signum, frame) -> None:  # type: ignore[return-type]
    """Terminate child processes gracefully on container stop."""
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    for proc in processes:
        if proc.poll() is None:
            proc.wait()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    start()
    for proc in processes:
        proc.wait()
