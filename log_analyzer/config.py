from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def _require_env(name: str) -> str:
    """Return the value of an environment variable or raise an error."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Variavel {name} nao definida")
    return value


# Parametros de conexao definidos exclusivamente via variáveis de ambiente
DB_HOST = _require_env("PG_HOST")
DB_PORT = int(_require_env("PG_PORT"))
DB_NAME = _require_env("PG_DB")
DB_USER = _require_env("PG_USER")
DB_PASSWORD = _require_env("PG_PASS")

LOG_FILE = Path(os.getenv("LOG_FILE", "rsyslog.log"))

SEVERITY_MODEL = _require_env("SEVERITY_MODEL")
ANOMALY_MODEL = _require_env("ANOMALY_MODEL")

# Modelo para deteccao de intrusoes em rede
NIDS_MODEL = _require_env("NIDS_MODEL")
NIDS_TOKENIZER = os.getenv("NIDS_TOKENIZER")
NET_LOG_FILE = Path(os.getenv("NET_LOG_FILE", "network.log"))
NET_INTERFACE = os.getenv("NET_INTERFACE")

# Model used for semantic anomaly detection via SentenceTransformers
SEMANTIC_MODEL = _require_env("SEMANTIC_MODEL")

# Modelo para analise de logs usando Hugging Face
HUGGINGFACE_MODEL = _require_env("HUGGINGFACE_MODEL")
# Tipo de dispositivo para o pipeline do Hugging Face: "cpu" ou "cuda"
DEVICE_TYPE = os.getenv("DEVICE_TYPE", "cpu")

# Instrucao base para compor o prompt enviado ao modelo de linguagem
LLM_PROMPT = os.getenv(
    "LLM_PROMPT",
    "Analise o log abaixo levando em conta o contexto fornecido e resuma possiveis causas ou acoes recomendadas. Me entregue o texto traduzido para o Portugues do Brasil (PT-BR).",
)

# Minimum score to treat a log as anomalous. The default value is
# conservative because the DistilBERT model was trained to separate
# normal lines from anomalies and may produce high scores for benign
# messages. Adjust this environment variable to be more or less
# sensitive.
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.8"))
