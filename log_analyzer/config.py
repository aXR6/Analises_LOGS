from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "logs")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

LOG_FILE = Path(os.getenv("LOG_FILE", "rsyslog.log"))

SEVERITY_MODEL = os.getenv(
    "SEVERITY_MODEL", "byviz/bylastic_classification_logs"
)
ANOMALY_MODEL = os.getenv(
    "ANOMALY_MODEL", "teoogherghi/Log-Analysis-Model-DistilBert"
)
