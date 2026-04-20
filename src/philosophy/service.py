from dataclasses import dataclass

from philosophy.config import Configuration

@dataclass(frozen=True)
class HealthSnapshot:
    status: str
    name: str
    collection_name: str
    embedding_model: str
    chat_model: str

class PhilosophyService:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def health(self) -> HealthSnapshot:
        return HealthSnapshot(
            status="ok",
            name=self.configuration.app.name,
            collection_name=self.configuration.app.collection_name,
            embedding_model=self.configuration.models.embedding_model,
            chat_model=self.configuration.models.chat_model,
        )
