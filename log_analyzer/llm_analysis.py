from typing import List
from transformers import pipeline

from .log_db import LogDB
from .config import HUGGINGFACE_MODEL, DEVICE_TYPE


_pipe = None


def _get_pipeline():
    global _pipe
    if _pipe is None:
        device = 0 if DEVICE_TYPE.lower() == "cuda" else -1
        _pipe = pipeline("text-generation", model=HUGGINGFACE_MODEL, device=device)
    return _pipe


def analyze_log(log_id: int, context: int = 5) -> str:
    """Analyze the log using a Hugging Face model and store the result."""
    db = LogDB()
    logs = db.get_log_with_context(log_id, context=context)
    if not logs:
        db.close()
        return "Log nao encontrado"
    messages = "\n".join(f"{ts} {host}: {msg}" for _, ts, host, msg in logs)
    prompt = (
        "Analise o log abaixo levando em conta o contexto fornecido e "
        "resuma possiveis causas ou acoes recomendadas.\n" + messages
    )
    try:
        pipe = _get_pipeline()
        result = pipe(prompt, max_new_tokens=200)[0]["generated_text"]
        db.insert_analysis(log_id, result)
        db.insert_analyzed_log(log_id, result)
        db.close()
        return result
    except Exception as exc:
        db.close()
        return f"Erro ao consultar o modelo: {exc}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analisa um log usando Hugging Face")
    parser.add_argument("log_id", type=int, help="ID do log no banco")
    parser.add_argument(
        "--context", type=int, default=5, help="Quantidade de linhas de contexto"
    )
    args = parser.parse_args()
    print(analyze_log(args.log_id, context=args.context))
