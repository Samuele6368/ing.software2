from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Registration:
    id: Optional[int]
    student_id: int
    exam_id: int
    #il voto inizialmente è None perché l'esame non è stato ancora sostenuto
    voto: Optional[int] = None
    #la lode inizialmente è 0, poi quando verrà assegnata diventerà 1
    lode: int = 0
    #appena creata la registrazionelo stato inizialmente è "iscritto", poi può diventare "completato" o "annullato"
    stato: str = "iscritto"

    def to_dict(self) -> dict:
        return asdict(self)
