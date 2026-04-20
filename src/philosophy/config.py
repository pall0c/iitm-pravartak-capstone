from dataclasses import dataclass

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
