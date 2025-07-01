import os
import requests
from typing import List

from .log_db import LogDB
from .config import OLLAMA_ENDPOINT, OLLAMA_MODEL


def analyze_log(log_id: int, context: int = 5) -> str:
    """Send the log with context to the configured Ollama endpoint."""
    db = LogDB()
    logs = db.get_log_with_context(log_id, context=context)
    db.close()
    if not logs:
        return "Log nao encontrado"
    messages = "\n".join(f"{ts} {host}: {msg}" for _, ts, host, msg in logs)
    prompt = (
        "Analise o log abaixo levando em conta o contexto fornecido e "
        "resuma possiveis causas ou acoes recomendadas.\n" + messages
    )
    try:
        resp = requests.post(
            OLLAMA_ENDPOINT,
            json={"model": OLLAMA_MODEL, "prompt": prompt},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
    except Exception as exc:
        return f"Erro ao consultar o modelo: {exc}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analisa um log usando Ollama")
    parser.add_argument("log_id", type=int, help="ID do log no banco")
    parser.add_argument(
        "--context", type=int, default=5, help="Quantidade de linhas de contexto"
    )
    args = parser.parse_args()
    print(analyze_log(args.log_id, context=args.context))
