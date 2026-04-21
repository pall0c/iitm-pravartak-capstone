from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from ..config import load_configuration
from ..schemas import AuthorOption, QueryRequest, QueryResponse
from ..service import PhilosophyService, QueryRejectedError

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


@app.get("/api/v1/health")
async def health_v1() -> dict:
    snapshot = service.health()
    return {
        "status": snapshot.status,
        "embedding_model": snapshot.embedding_model,
        "chat_model": snapshot.chat_model,
        "collection_name": snapshot.collection_name,
    }


@app.get("/api/v1/authors", response_model=list[AuthorOption])
async def authors_v1() -> list[dict[str, str]]:
    return service.authors()


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(payload: QueryRequest) -> QueryResponse:
    try:
        return await service.answer(
            question=payload.question,
            author_key=payload.author_key,
            top_k=payload.top_k,
        )
    except QueryRejectedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/query/stream")
async def stream_query(payload: QueryRequest) -> StreamingResponse:
    try:
        event_stream = service.stream_events(
            question=payload.question,
            author_key=payload.author_key,
            top_k=payload.top_k,
        )
    except QueryRejectedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StreamingResponse(event_stream, media_type="application/x-ndjson")
