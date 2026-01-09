from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Registration:
    id: Optional[int]
    student_id: int
    exam_id: int
    voto: Optional[int] = None
    lode: int = 0
    stato: str = "iscritto"

    def to_dict(self) -> dict:
        return asdict(self)
