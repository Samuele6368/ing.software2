from __future__ import annotations

from typing import List, Optional

from db.database import get_connection


def _sanitize(text: str) -> str: #rimuove spazi bianchi iniziali e finali
    return text.strip()

def _validate_matricola_format(matricola: str) -> None:
    """Valida che la matricola contenga solo cifre e rappresenti un intero positivo."""
    matricola_stripped = matricola.strip()
    if not matricola_stripped:
        raise ValueError("Formato non valido: la matricola deve essere un numero intero.")
    if not matricola_stripped.isdigit():
        raise ValueError("Formato non valido: la matricola deve essere un numero intero.")
    # Verifica che il numero sia positivo (isdigit() garantisce che sia un numero valido)
    if int(matricola_stripped) <= 0:
        raise ValueError("Formato non valido: la matricola deve essere un numero intero.")

#Logica di business
def _validate_student_fields(matricola: str, nome: str, cognome: str) -> None:
    _validate_matricola_format(matricola)
    if not nome.strip():
        raise ValueError("Nome obbligatorio.")
    if not cognome.strip():
        raise ValueError("Cognome obbligatorio.")


def create_student(matricola: str, nome: str, cognome: str) -> dict:
    _validate_student_fields(matricola, nome, cognome)
    matricola_clean = _sanitize(matricola)
    nome_clean = _sanitize(nome)
    cognome_clean = _sanitize(cognome)
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM students WHERE matricola = ?", (matricola_clean,)).fetchone() #controlla se la matricola esiste già
        if exists:
            raise ValueError("Matricola già esistente.")
        cur = conn.execute(
            "INSERT INTO students (matricola, nome, cognome) VALUES (?, ?, ?)", #esegue l'inserimento del dato nel database
            (matricola_clean, nome_clean, cognome_clean),
        )
        conn.commit() #conferma le modifiche
        return {
            "id": cur.lastrowid,
            "matricola": matricola_clean,
            "nome": nome_clean,
            "cognome": cognome_clean,
        }


def get_student_by_matricola(matricola: str) -> Optional[dict]:
    matricola_clean = _sanitize(matricola)
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM students WHERE matricola = ?", (matricola_clean,)).fetchone()
        return dict(row) if row else None


def update_student(matricola: str, nome: str, cognome: str) -> dict:
    _validate_student_fields(matricola, nome, cognome)
    matricola_clean = _sanitize(matricola)
    nome_clean = _sanitize(nome)
    cognome_clean = _sanitize(cognome)
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE students SET nome = ?, cognome = ? WHERE matricola = ?",
            (nome_clean, cognome_clean, matricola_clean),
        )
        if cur.rowcount == 0:
            raise ValueError("Studente non trovato.")
        conn.commit()
    updated = get_student_by_matricola(matricola_clean)
    if not updated:
        raise ValueError("Studente non trovato dopo l'aggiornamento.")
    return updated


def delete_student(matricola: str) -> None:
    matricola_clean = _sanitize(matricola)
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM students WHERE matricola = ?", (matricola_clean,))
        if cur.rowcount == 0:
            raise ValueError("Student not found.")
        conn.commit()


def list_students() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY cognome, nome").fetchall()
        return [dict(row) for row in rows]