# Philosophy RAG

A local retrieval-augmented generation project for querying a small philosophy corpus through a FastAPI backend and a Next.js frontend.

The current corpus includes:
1. Plato, *Republic*
1. Seneca, *On the Shortness of Life*
1. Marcus Aurelius, *Meditations*

Downloaded from [Internet Archive](https://archive.org)

## Prerequisites

Install and verify these tools before starting:

1. [`bun`](https://bun.sh/) for the frontend
1. [`uv`](https://docs.astral.sh/uv/) for Python dependency management
1. [`ollama`](https://ollama.com/) for local embedding and chat models

You will also need Python `3.13+`.

Pull the models referenced by `config.yaml` before ingesting or querying:

```bash
ollama pull qwen3-embedding:0.6b
ollama pull qwen3.5:4b
```

Start Ollama locally:

```bash
ollama serve
```

## Project Structure

```text
.
├── config.yaml                # Runtime configuration: app, models, ingestion, catalog
├── data/                      # Source PDFs and generated Chroma vector store
├── main.py                    # CLI entrypoint for ingestion
├── src/philosophy/
│   ├── api/                   # FastAPI app and routes
│   ├── pipelines/             # Embedding, retrieval, and generation pipelines
│   ├── catalog.py             # Document catalog and author metadata helpers
│   ├── config.py              # YAML configuration loader
│   ├── schemas.py             # API request/response models
│   └── service.py             # Orchestration layer used by the API and CLI
└── www/                       # Next.js frontend
```

## Configuration

The backend loads settings from `config.yaml`.

Key values to review:

1. `app.data_dir`: where source PDFs are discovered
1. `app.vector_store_dir`: where Chroma persists embeddings
1. `models.embedding_model`: Ollama embedding model
1. `models.chat_model`: Ollama chat model
1. `models.ollama_base_url`: Ollama server URL
1. `catalog.documents`: metadata used for author filters and source attribution

If you add or remove PDFs, update `catalog.documents` so the UI and citations stay accurate.

## Getting Started

### 1. Install backend dependencies

```bash
uv sync
```

### 2. Build or rebuild the vector store

```bash
uv run main.py --reset
```

This ingests PDFs from `data/` and writes the Chroma database to `data/chroma_db`.

### 3. Start the API

```bash
uv run fastapi dev
```

The backend serves on `http://127.0.0.1:8000` by default.

Useful endpoints:

1. `GET /api/health`
1. `GET /api/v1/authors`
1. `POST /api/v1/query`
1. `POST /api/v1/query/stream`

### 4. Install frontend dependencies

```bash
cd www
bun i
```

### 5. Start the web app

```bash
bun dev
```
