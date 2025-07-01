import argparse
from pathlib import Path
import re
from typing import List, Tuple

from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np
from log_analyzer.config import SEMANTIC_MODEL

# Regex similar ao usado no parser principal para extrair a mensagem
SYSLOG_RE = re.compile(r'^(?P<month>\w{3})\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\s+(?P<msg>.*)$')
ISO_RE = re.compile(r'^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))\s+\S+\s+(?P<msg>.*)$')


def extract_messages(file_path: Path) -> List[str]:
    messages: List[str] = []
    with file_path.open('r') as f:
        for line in f:
            m = SYSLOG_RE.match(line)
            if m:
                messages.append(m.group('msg'))
                continue
            m = ISO_RE.match(line)
            if m:
                messages.append(m.group('msg'))
            else:
                messages.append(line.strip())
    return messages


def detect_anomalies(messages: List[str], eps: float = 0.5, min_samples: int = 5) -> Tuple[np.ndarray, DBSCAN]:
    """Retorna labels do DBSCAN para cada mensagem."""
    model = SentenceTransformer(SEMANTIC_MODEL)
    embeddings = model.encode(messages, convert_to_numpy=True, show_progress_bar=False)
    clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(embeddings)
    return clusterer.labels_, clusterer


class OnlineSemanticDetector:
    """Incrementally detect semantic anomalies using DBSCAN."""

    def __init__(self, eps: float = 0.5, min_samples: int = 5, model_name: str = SEMANTIC_MODEL):
        self.eps = eps
        self.min_samples = min_samples
        self.model = SentenceTransformer(model_name)
        self.messages: List[str] = []
        self.labels: List[int] = []

    def add(self, msg: str) -> bool:
        """Add a message and return True if it is an outlier."""
        self.messages.append(msg)
        embeddings = self.model.encode(self.messages, convert_to_numpy=True, show_progress_bar=False)
        clusterer = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='cosine').fit(embeddings)
        self.labels = clusterer.labels_.tolist()
        return self.labels[-1] == -1


def main() -> None:
    parser = argparse.ArgumentParser(description="Deteccao de anomalias semanticas em logs")
    parser.add_argument('log_file', help='Arquivo de log a ser analisado')
    parser.add_argument('--eps', type=float, default=0.5, help='Parametro eps do DBSCAN')
    parser.add_argument('--min-samples', type=int, default=5, help='Parametro min_samples do DBSCAN')
    args = parser.parse_args()

    messages = extract_messages(Path(args.log_file))
    labels, _ = detect_anomalies(messages, eps=args.eps, min_samples=args.min_samples)

    for idx, (msg, label) in enumerate(zip(messages, labels)):
        tag = 'ANOMALIA' if label == -1 else f'cluster {label}'
        print(f"{idx}\t{tag}\t{msg}")


if __name__ == '__main__':
    main()
