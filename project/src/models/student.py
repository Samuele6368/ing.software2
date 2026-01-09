from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Student:
    id: Optional[int]
    matricola: str
    nome: str
    cognome: str

    def to_dict(self) -> dict:
        return asdict(self)
