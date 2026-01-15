from __future__ import annotations

from typing import List, Optional

from db.database import get_connection

#crea corso nel database
def create_course(codice: str, nome: str, cfu: int) -> dict:
    codice_clean = codice.strip()
    nome_clean = nome.strip()
    if not codice_clean:
        raise ValueError("Codice corso obbligatorio.")
    if not nome_clean:
        raise ValueError("Nome corso obbligatorio.")
    if cfu <= 0:
        raise ValueError("I CFU devono essere maggiori di zero.")
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM courses WHERE codice = ?", (codice_clean,)).fetchone()
        if exists:
            raise ValueError("Codice corso già esistente.")
        cur = conn.execute(
            "INSERT INTO courses (codice, nome, cfu) VALUES (?, ?, ?)",
            (codice_clean, nome_clean, cfu),
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "codice": codice_clean,
            "nome": nome_clean,
            "cfu": cfu,
        }


def list_courses() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM courses ORDER BY nome").fetchall()
        return [dict(row) for row in rows]


def get_course_by_codice(codice: str) -> Optional[dict]:
    codice_clean = codice.strip()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM courses WHERE codice = ?", (codice_clean,)).fetchone()
        return dict(row) if row else None


def delete_course(codice: str) -> None:
    codice_clean = codice.strip()
    if not codice_clean:
        raise ValueError("Codice corso obbligatorio.")
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM courses WHERE codice = ?", (codice_clean,))
        if cur.rowcount == 0:
            raise ValueError("Course not found.")
        conn.commit()
