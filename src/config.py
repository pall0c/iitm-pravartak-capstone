from dataclasses import dataclass
from pathlib import Path

import yaml

from .catalog import CatalogEntry, PhilosophyCatalog


@dataclass(frozen=True)
class AppConfig:
    name: str
    collection_name: str
    data_dir: Path
    vector_store_dir: Path


@dataclass(frozen=True)
class ModelConfig:
    embedding_model: str
    chat_model: str
    ollama_base_url: str


@dataclass(frozen=True)
class IngestionConfig:
    chunk_size: int
    chunk_overlap: int
    batch_size: int
    top_k: int


@dataclass(frozen=True)
class Configuration:
    app: AppConfig
    models: ModelConfig
    ingestion: IngestionConfig
    catalog: PhilosophyCatalog


def _load_yaml(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_configuration() -> Configuration:
    payload = _load_yaml(Path("./config.yaml"))
    app_payload = payload["app"]
    model_payload = payload["models"]
    catalog_payload = payload["catalog"]["documents"]
    ingestion_payload = payload["ingestion"]

    app = AppConfig(
        name=app_payload["name"],
        collection_name=app_payload["collection_name"],
        data_dir=Path(app_payload["data_dir"]).resolve(),
        vector_store_dir=Path(app_payload["vector_store_dir"]).resolve(),
    )
    models = ModelConfig(
        embedding_model=model_payload["embedding_model"],
        chat_model=model_payload["chat_model"],
        ollama_base_url=model_payload["ollama_base_url"],
    )
    ingestion = IngestionConfig(
        chunk_size=int(ingestion_payload["chunk_size"]),
        chunk_overlap=int(ingestion_payload["chunk_overlap"]),
        batch_size=int(ingestion_payload["batch_size"]),
        top_k=int(ingestion_payload["top_k"]),
    )
    catalog = PhilosophyCatalog(
        CatalogEntry(
            key=entry["key"],
            author=entry["author"],
            work=entry["work"],
            path=Path(entry["path"]).resolve(),
        )
        for entry in catalog_payload
    )

    return Configuration(app=app, models=models, ingestion=ingestion, catalog=catalog)
