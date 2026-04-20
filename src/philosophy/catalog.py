from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Union

@dataclass(frozen=True)
class CatalogEntry:
    path: Path
    key: str
    author: str
    work: str

class PhilosophyCatalog:
    def __init__(self, entries: Iterable[CatalogEntry]) -> None:
        self._entries = list(entries)
        self._by_key = {entry.key: entry for entry in self._entries}
        self._by_path = {entry.path.resolve(): entry for entry in self._entries}

    def match(self, file_path: Union[str, Path]) -> Optional[CatalogEntry]:
        return self._by_path.get(Path(file_path).resolve())

    def get(self, key: str) -> Optional[CatalogEntry]:
        return self._by_key.get(key.strip().lower())

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
