from pathlib import Path
from typing import Protocol


class IDocumentReader(Protocol):
    def read(self, path: Path) -> list[tuple[int, str]]: ...
