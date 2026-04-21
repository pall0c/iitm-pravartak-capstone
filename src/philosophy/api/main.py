from fastapi import FastAPI

from ..config import load_configuration
from ..service import PhilosophyService

config = load_configuration()
service = PhilosophyService(config)

app = FastAPI(title=config.app.name, version="0.1.0")


@app.get("/api")
async def root():
    return {"Hello": "Philosophy API!"}


@app.get("/api/health")
async def health() -> dict:
    snapshot = service.health()
    return {
        "status": snapshot.status,
        "name": snapshot.name,
        "collection_name": snapshot.collection_name,
        "embedding_model": snapshot.embedding_model,
        "chat_model": snapshot.chat_model,
    }


@app.get("/api/authors")
async def authors() -> list[dict[str, str]]:
    return service.authors()
