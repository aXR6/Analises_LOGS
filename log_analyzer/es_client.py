from __future__ import annotations

from elasticsearch import Elasticsearch
from .config import ES_URL

_client: Elasticsearch | None = None

def get_client() -> Elasticsearch:
    global _client
    if _client is None:
        _client = Elasticsearch(ES_URL)
    return _client

def index_log(log_id: int, document: dict) -> None:
    es = get_client()
    es.index(index="logs", id=log_id, document=document)

def search_logs(query: str, limit: int = 100, page: int | None = None) -> list[int]:
    es = get_client()
    body = {"query": {"match": {"message": query}}}
    from_ = (page - 1) * limit if page is not None else 0
    resp = es.search(index="logs", body=body, from_=from_, size=limit)
    return [int(hit["_id"]) for hit in resp["hits"]["hits"]]
