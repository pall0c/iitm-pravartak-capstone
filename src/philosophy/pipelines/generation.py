from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from ..config import Configuration

SYSTEM_PROMPT = """You are a philosophy research assistant.

Answer only from the retrieved passages.
If the passages are insufficient, say that the indexed texts do not provide enough evidence.
Stay within philosophy and do not invent outside facts.
Reference the author and work when you can do so directly from the passages.
"""


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            content_item = cast(Mapping[str, object], item)
            if content_item.get("type") != "text":
                continue
            text = content_item.get("text")
            if isinstance(text, str):
                text_parts.append(text)
        return "".join(text_parts)
    return ""


class GenerationPipeline:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.llm = ChatOllama(
            model=configuration.models.chat_model,
            base_url=configuration.models.ollama_base_url,
            temperature=0.2,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    "Question:\n{question}\n\nRetrieved passages:\n{context}\n\n"
                    "Write a concise answer grounded only in those passages.",
                ),
            ]
        )

    @staticmethod
    def format_context(documents: list[Document]) -> str:
        rendered_chunks: list[str] = []
        for index, document in enumerate(documents, start=1):
            rendered_chunks.append(
                f"[{index}] {document.metadata['author']} | {document.metadata['work']} | "
                f"page {document.metadata['page']}\n{document.page_content.strip()}"
            )
        return "\n\n".join(rendered_chunks)

    async def answer(self, question: str, documents: list[Document]) -> str:
        messages = self.prompt.format_messages(
            question=question,
            context=self.format_context(documents),
        )
        response = await self.llm.ainvoke(messages)
        return _content_to_text(response.content).strip()

    async def stream(self, question: str, documents: list[Document]):
        messages = self.prompt.format_messages(
            question=question,
            context=self.format_context(documents),
        )
        async for chunk in self.llm.astream(messages):
            text = _content_to_text(chunk.content)
            if text:
                yield text
