import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .catalog import PhilosophyCatalog, CatalogEntry

@dataclass(frozen=True)
class AppConfig:
    name: str
    collection_name: str

@dataclass(frozen=True)
class ModelConfig:
    embedding_model: str
    chat_model: str

@dataclass(frozen=True)
class Configuration:
    app: AppConfig
    models: ModelConfig
    catalog: PhilosophyCatalog

def _load_yaml(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}

def load_configuration() -> Configuration:
    payload = _load_yaml(Path('./config.yaml'))
    app_payload = payload["app"]
    model_payload = payload["models"]
    catalog_payload = payload["catalog"]["documents"]

    app = AppConfig(
        name=app_payload["name"],
        collection_name=app_payload["collection_name"]
    )
    models = ModelConfig(
        embedding_model=model_payload["embedding_model"],
        chat_model=model_payload["chat_model"],
    )
    catalog = PhilosophyCatalog(
        CatalogEntry(
            key=entry["key"],
            author=entry["author"],
            work=entry["work"],
            path=Path(entry["path"]).resolve()
        )
        for entry in catalog_payload
    )

    return Configuration(app=app, models=models, catalog=catalog)
