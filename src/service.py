from __future__ import annotations

import json
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable, Optional

from langchain_core.documents import Document

from .catalog import PhilosophyCatalog
from .config import Configuration
from .pipelines.embedding import EmbeddingPipeline, IngestionReport
from .pipelines.generation import GenerationPipeline
from .pipelines.retrieval import RetrievalPipeline
from .schemas import QueryResponse, SourceHit


@dataclass(frozen=True)
class HealthSnapshot:
    status: str
    name: str
    collection_name: str
    embedding_model: str
    chat_model: str


class QueryRejectedError(ValueError):
    pass


class PhilosophyService:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.catalog: PhilosophyCatalog = configuration.catalog
        self._embedding_pipeline: Optional[EmbeddingPipeline] = None
        self._retrieval_pipeline: Optional[RetrievalPipeline] = None
        self._generation_pipeline: Optional[GenerationPipeline] = None

    @property
    def embedding_pipeline(self) -> EmbeddingPipeline:
        if self._embedding_pipeline is None:
            self._embedding_pipeline = EmbeddingPipeline(self.configuration)
        return self._embedding_pipeline

    @property
    def retrieval_pipeline(self) -> RetrievalPipeline:
        if self._retrieval_pipeline is None:
            self._retrieval_pipeline = RetrievalPipeline(self.configuration)
        return self._retrieval_pipeline

    @property
    def generation_pipeline(self) -> GenerationPipeline:
        if self._generation_pipeline is None:
            self._generation_pipeline = GenerationPipeline(self.configuration)
        return self._generation_pipeline

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

    def _normalize_author(self, author_key: Optional[str]) -> Optional[str]:
        normalized = self.catalog.normalize_author_key(author_key)
        if author_key and not normalized:
            raise QueryRejectedError(f"Unknown author filter: {author_key}")
        return normalized

    def _source_hits(self, documents: Iterable[Document]) -> list[SourceHit]:
        source_hits: list[SourceHit] = []
        for document in documents:
            metadata = document.metadata
            source_hits.append(
                SourceHit(
                    author=str(metadata["author"]),
                    author_key=str(metadata["author_key"]),
                    work=str(metadata["work"]),
                    source_file=str(metadata["source_file"]),
                    page=int(metadata["page"]),
                    excerpt=document.page_content.strip().replace("\n", " ")[:280],
                )
            )
        return source_hits

    def _retrieve_documents(
        self,
        question: str,
        author_key: Optional[str],
        top_k: Optional[int],
    ) -> list[Document]:
        normalized_author = self._normalize_author(author_key)

        if not self.retrieval_pipeline.has_documents():
            raise QueryRejectedError(
                "The vector store is empty. Run the ingest step before querying."
            )

        documents = self.retrieval_pipeline.search(
            question, author_key=normalized_author, top_k=top_k
        )
        if not documents:
            raise QueryRejectedError(
                "I couldn't find relevant passages in the indexed philosophy texts for that question."
            )
        return documents

    async def answer(
        self,
        question: str,
        author_key: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> QueryResponse:
        documents = self._retrieve_documents(question, author_key, top_k)
        answer = await self.generation_pipeline.answer(question, documents)
        return QueryResponse(answer=answer, sources=self._source_hits(documents))

    def stream_events(
        self,
        question: str,
        author_key: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        documents = self._retrieve_documents(question, author_key, top_k)
        sources = [source.model_dump() for source in self._source_hits(documents)]

        async def event_stream() -> AsyncGenerator[str, None]:
            yield json.dumps({"type": "context", "sources": sources}) + "\n"

            async for token in self.generation_pipeline.stream(question, documents):
                yield json.dumps({"type": "token", "token": token}) + "\n"

            yield json.dumps({"type": "done"}) + "\n"

        return event_stream()
