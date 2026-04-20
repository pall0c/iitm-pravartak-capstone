from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import Configuration

@dataclass(frozen=True)
class IngestionReport:
    pdf_count: int
    page_count: int
    chunk_count: int
    persist_directory: str

class EmbeddingPipeline:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.catalog = configuration.catalog
        self.embeddings = OllamaEmbeddings(
            model=configuration.models.embedding_model,
            base_url=configuration.models.ollama_base_url,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=configuration.ingestion.chunk_size,
            chunk_overlap=configuration.ingestion.chunk_overlap,
        )

    def discover_pdfs(self) -> list[Path]:
        return sorted(self.configuration.app.data_dir.rglob("*.pdf"))

    def _build_page_documents(self, pdf_path: Path) -> list[Document]:
        entry = self.catalog.match(pdf_path)
        loader = PyPDFLoader(str(pdf_path), mode="page")
        page_documents = loader.load()

        author = entry.author if entry else "Unknown"
        author_key = entry.key if entry else "unknown"
        work = entry.work if entry else pdf_path.stem.replace("-", " ").title()

        enriched: list[Document] = []
        for page_document in page_documents:
            page_number = int(page_document.metadata.get("page", 0)) + 1
            metadata = {
                "author": author,
                "author_key": author_key,
                "work": work,
                "source_file": pdf_path.name,
                "source_path": str(pdf_path),
                "page": page_number,
            }
            enriched.append(Document(page_content=page_document.page_content, metadata=metadata))
        return enriched

    def load_documents(self) -> list[Document]:
        documents: list[Document] = []
        for pdf_path in self.discover_pdfs():
            documents.extend(self._build_page_documents(pdf_path))
        return documents

    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        chunks = self.splitter.split_documents(documents)
        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index
            chunk.metadata["chunk_id"] = (
                f"{chunk.metadata['author_key']}-{chunk.metadata['source_file']}-{chunk.metadata['page']}-{index}"
            )
        return chunks

    def ingest(self, reset: bool = False) -> IngestionReport:
        pdfs = self.discover_pdfs()
        if not pdfs:
            raise ValueError(f"No PDFs found under {self.configuration.app.data_dir}")

        documents = self.load_documents()
        chunks = self.chunk_documents(documents)

        persist_directory = self.configuration.app.vector_store_dir
        if reset and persist_directory.exists():
            shutil.rmtree(persist_directory)
        persist_directory.mkdir(parents=True, exist_ok=True)

        vector_store = Chroma(
            collection_name=self.configuration.app.collection_name,
            persist_directory=str(persist_directory),
            embedding_function=self.embeddings,
        )
        for start in range(0, len(chunks), self.configuration.ingestion.batch_size):
            batch = chunks[start : start + self.configuration.ingestion.batch_size]
            vector_store.add_documents(
                documents=batch,
                ids=[chunk.metadata["chunk_id"] for chunk in batch],
            )

        return IngestionReport(
            pdf_count=len(pdfs),
            page_count=len(documents),
            chunk_count=len(chunks),
            persist_directory=str(persist_directory),
        )
