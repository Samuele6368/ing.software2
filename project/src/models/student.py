from __future__ import annotations


from dataclasses import asdict, dataclass
from typing import Optional

#genera una classe Student con i campi id, matricola, nome, cognome in automatico senza dover specificare ogni campo
@dataclass
class Student:
    # L'ID è Optional perché quando creo un nuovo studente in memoria non ha ancora un ID. L'ID gli verrà dato dal databse dopo il salvataggio.
    id: Optional[int]
    matricola: str
    nome: str
    cognome: str

    def to_dict(self) -> dict:
        return asdict(self)
