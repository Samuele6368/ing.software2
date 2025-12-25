from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Exam:
    id: Optional[int]
    course_id: int
    data_appello: str

    def to_dict(self) -> dict:
        return asdict(self)
