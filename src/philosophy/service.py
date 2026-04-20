from dataclasses import dataclass
from typing import Optional

from .config import Configuration
from .catalog import PhilosophyCatalog
from .pipelines.embedding import EmbeddingPipeline, IngestionReport

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
        self.catalog: PhilosophyCatalog = configuration.catalog
        self._embedding_pipeline: Optional[EmbeddingPipeline] = None

    @property
    def embedding_pipeline(self) -> EmbeddingPipeline:
        if self._embedding_pipeline is None:
            self._embedding_pipeline = EmbeddingPipeline(self.configuration)
        return self._embedding_pipeline

    def health(self) -> HealthSnapshot:
        return HealthSnapshot(
            status="ok",
            name=self.configuration.app.name,
            collection_name=self.configuration.app.collection_name,
            embedding_model=self.configuration.models.embedding_model,
            chat_model=self.configuration.models.chat_model,
        )

    def authors(self) -> list[dict[str, str]]:
        return self.catalog.author_options()

    def ingest(self, reset: bool = False) -> IngestionReport:
        return self.embedding_pipeline.ingest(reset=reset)
