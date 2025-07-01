from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Parametros de conexao com valores padrao do banco principal
DB_HOST = os.getenv("PG_HOST", "172.16.187.133")
DB_PORT = int(os.getenv("PG_PORT", "5432"))
DB_NAME = os.getenv("PG_DB", "resultscan")
DB_USER = os.getenv("PG_USER", "vector_store")
DB_PASSWORD = os.getenv("PG_PASS", "902grego1989")

LOG_FILE = Path(os.getenv("LOG_FILE", "rsyslog.log"))

SEVERITY_MODEL = os.getenv(
    "SEVERITY_MODEL", "byviz/bylastic_classification_logs"
)
ANOMALY_MODEL = os.getenv(
    "ANOMALY_MODEL", "teoogherghi/Log-Analysis-Model-DistilBert"
)
