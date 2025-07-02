import os
import subprocess

from log_analyzer.config import NET_LOG_FILE


def main() -> None:
    interface = os.getenv("NET_INTERFACE")
    if not interface:
        print("Variavel NET_INTERFACE nao definida.")
        return
    path = NET_LOG_FILE
    path.touch(exist_ok=True)
    with path.open("a") as f:
        proc = subprocess.Popen(
            ["tcpdump", "-n", "-l", "-i", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        try:
            for line in proc.stdout:
                f.write(line)
                f.flush()
        except KeyboardInterrupt:
            pass
        finally:
            proc.terminate()
            proc.wait()


if __name__ == "__main__":
    main()
