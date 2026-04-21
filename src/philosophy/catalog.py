from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Union


@dataclass(frozen=True)
class CatalogEntry:
    key: str
    author: str
    work: str
    path: Path


class PhilosophyCatalog:
    def __init__(self, entries: Iterable[CatalogEntry]) -> None:
        self._entries = list(entries)
        self._by_key = {entry.key: entry for entry in self._entries}
        self._by_path = {
            entry.path.resolve(): entry for entry in self._entries if entry.path is not None
        }

    def match(self, file_path: Union[str, Path]) -> Optional[CatalogEntry]:
        resolved_path = Path(file_path).resolve()
        return self._by_path.get(resolved_path)

    def normalize_author_key(self, author_key: Optional[str]) -> Optional[str]:
        if not author_key:
            return None
        key = author_key.strip().lower()
        return key if key in self._by_key else None

    def entries(self) -> list[CatalogEntry]:
        return list(self._entries)

    def author_options(self) -> list[dict[str, str]]:
        return [
            {
                "key": entry.key,
                "author": entry.author,
                "work": entry.work,
            }
            for entry in self._entries
        ]
