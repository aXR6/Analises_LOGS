from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

LOG_DB_PATH = Path(os.getenv("LOG_DB_PATH", "logs.db"))
LOG_FILE = Path(os.getenv("LOG_FILE", "rsyslog.log"))
SEVERITY_MODEL = os.getenv(
    "SEVERITY_MODEL", "byviz/bylastic_classification_logs"
)
ANOMALY_MODEL = os.getenv(
    "ANOMALY_MODEL", "teoogherghi/Log-Analysis-Model-DistilBert"
)

