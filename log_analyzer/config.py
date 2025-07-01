from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Allow alternative environment variable prefix ``PG_`` for compatibility
DB_HOST = os.getenv("PG_HOST") or os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("PG_PORT") or os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("PG_DB") or os.getenv("DB_NAME", "logs")
DB_USER = os.getenv("PG_USER") or os.getenv("DB_USER")
DB_PASSWORD = os.getenv("PG_PASS") or os.getenv("DB_PASSWORD")

LOG_FILE = Path(os.getenv("LOG_FILE", "rsyslog.log"))

SEVERITY_MODEL = os.getenv(
    "SEVERITY_MODEL", "byviz/bylastic_classification_logs"
)
ANOMALY_MODEL = os.getenv(
    "ANOMALY_MODEL", "teoogherghi/Log-Analysis-Model-DistilBert"
)
