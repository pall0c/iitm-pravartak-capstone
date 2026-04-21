from __future__ import annotations

from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from ..config import Configuration

class RetrievalPipeline:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.embeddings = OllamaEmbeddings(
            model=configuration.models.embedding_model,
            base_url=configuration.models.ollama_base_url,
        )
        self.vector_store = Chroma(
            collection_name=configuration.app.collection_name,
            persist_directory=str(configuration.app.vector_store_dir),
            embedding_function=self.embeddings,
        )

    def has_documents(self) -> bool:
        try:
            snapshot = self.vector_store.get(limit=1, include=[])
        except Exception:
            return False
        return bool(snapshot.get("ids"))

    def search(
        self,
        query: str,
        author_key: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> list[Document]:
        filter_payload = {"author_key": author_key} if author_key else None
        target_k = top_k or self.configuration.ingestion.top_k
        return self.vector_store.similarity_search(
            query,
            k=max(target_k * 5, target_k),
            filter=filter_payload,
        )
