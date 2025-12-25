from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from db.database import get_connection

DATE_FORMAT = "%Y-%m-%d"


def _validate_date(date_str: str) -> None:
    try:
        datetime.strptime(date_str, DATE_FORMAT)
    except ValueError as exc:
        raise ValueError("Data appello non valida. Usa il formato YYYY-MM-DD.") from exc


def _get_course(conn, course_codice: str):
    return conn.execute("SELECT * FROM courses WHERE codice = ?", (course_codice.strip(),)).fetchone()


def create_exam(course_codice: str, data_appello: str) -> dict:
    course_codice_clean = course_codice.strip()
    data_clean = data_appello.strip()
    if not course_codice_clean:
        raise ValueError("Codice corso obbligatorio.")
    if not data_clean:
        raise ValueError("Data appello obbligatoria.")
    _validate_date(data_clean)
    with get_connection() as conn:
        course = _get_course(conn, course_codice_clean)
        if not course:
            raise ValueError("Corso non trovato.")
        existing = conn.execute(
            "SELECT exams.id FROM exams JOIN courses ON exams.course_id = courses.id "
            "WHERE courses.codice = ? AND exams.data_appello = ?",
            (course_codice_clean, data_clean),
        ).fetchone()
        if existing:
            raise ValueError("Esiste già un appello per questo corso in questa data.")
        cur = conn.execute(
            "INSERT INTO exams (course_id, data_appello) VALUES (?, ?)",
            (course["id"], data_clean),
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "course_id": course["id"],
            "course_codice": course_codice_clean,
            "data_appello": data_clean,
        }


def list_exams(course_codice: Optional[str] = None) -> List[dict]:
    base_query = (
        "SELECT exams.id, exams.data_appello, courses.codice, courses.nome "
        "FROM exams JOIN courses ON exams.course_id = courses.id"
    )
    params: Tuple[str, ...] = ()
    if course_codice:
        base_query += " WHERE courses.codice = ?"
        params = (course_codice.strip(),)
    base_query += " ORDER BY exams.data_appello"
    with get_connection() as conn:
        rows = conn.execute(base_query, params).fetchall()
        return [
            {
                "id": row["id"],
                "course_codice": row["codice"],
                "course_nome": row["nome"],
                "data_appello": row["data_appello"],
            }
            for row in rows
        ]


def get_exam(course_codice: str, data_appello: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT exams.*, courses.codice, courses.nome FROM exams "
            "JOIN courses ON exams.course_id = courses.id "
            "WHERE courses.codice = ? AND exams.data_appello = ?",
            (course_codice.strip(), data_appello),
        ).fetchone()
        return dict(row) if row else None


def delete_exam(course_codice: str, data_appello: str) -> None:
    course_codice_clean = course_codice.strip()
    data_clean = data_appello.strip()
    if not course_codice_clean or not data_clean:
        raise ValueError("Course code and exam date are required.")
    with get_connection() as conn:
        exam = conn.execute(
            "SELECT exams.id FROM exams JOIN courses ON exams.course_id = courses.id "
            "WHERE courses.codice = ? AND exams.data_appello = ?",
            (course_codice_clean, data_clean),
        ).fetchone()
        if not exam:
            raise ValueError("Exam not found.")
        conn.execute("DELETE FROM exams WHERE id = ?", (exam["id"],))
        conn.commit()
