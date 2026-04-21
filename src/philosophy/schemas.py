from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AuthorOption(BaseModel):
    key: str
    author: str
    work: str


class SourceHit(BaseModel):
    author: str
    author_key: str
    work: str
    source_file: str
    page: int
    excerpt: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    author_key: Optional[str] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceHit]
