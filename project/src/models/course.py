from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Course:
    id: Optional[int]
    codice: str
    nome: str
    cfu: int

    def to_dict(self) -> dict:
        return asdict(self)
