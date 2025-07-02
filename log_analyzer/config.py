from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Parametros de conexao definidos exclusivamente via variáveis de ambiente
DB_HOST = os.getenv("PG_HOST")
DB_PORT = int(os.getenv("PG_PORT"))
DB_NAME = os.getenv("PG_DB")
DB_USER = os.getenv("PG_USER")
DB_PASSWORD = os.getenv("PG_PASS")

LOG_FILE = Path(os.getenv("LOG_FILE", "rsyslog.log"))

SEVERITY_MODEL = os.getenv(
    "SEVERITY_MODEL", "byviz/bylastic_classification_logs"
)
ANOMALY_MODEL = os.getenv(
    "ANOMALY_MODEL", "teoogherghi/Log-Analysis-Model-DistilBert"
)

# Modelo para deteccao de intrusoes em rede
NIDS_MODEL = os.getenv(
    "NIDS_MODEL", "SilverDragon9/Sniffer.AI"
)
NIDS_TOKENIZER = os.getenv("NIDS_TOKENIZER")
NET_LOG_FILE = Path(os.getenv("NET_LOG_FILE", "network.log"))

# Model used for semantic anomaly detection via SentenceTransformers
SEMANTIC_MODEL = os.getenv("SEMANTIC_MODEL", "all-MiniLM-L6-v2")

# Modelo para analise de logs usando Hugging Face
HUGGINGFACE_MODEL = os.getenv(
    "HUGGINGFACE_MODEL", "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
)
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
