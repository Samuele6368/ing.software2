from __future__ import annotations

from typing import Dict, List

from db.database import get_connection

VALID_VOTO_RANGE = range(18, 32)


def _fetch_student(conn, matricola: str):
    return conn.execute("SELECT * FROM students WHERE matricola = ?", (matricola.strip(),)).fetchone()


def _fetch_exam(conn, course_codice: str, data_appello: str):
    return conn.execute(
        "SELECT exams.id, exams.data_appello, courses.codice, courses.nome, courses.cfu "
        "FROM exams JOIN courses ON exams.course_id = courses.id "
        "WHERE courses.codice = ? AND exams.data_appello = ?",
        (course_codice.strip(), data_appello),
    ).fetchone()


def enroll_student(student_matricola: str, course_codice: str, data_appello: str) -> dict:
    student_clean = student_matricola.strip()
    course_clean = course_codice.strip()
    date_clean = data_appello.strip()
    if not student_clean:
        raise ValueError("Matricola obbligatoria.")
    if not course_clean:
        raise ValueError("Codice corso obbligatorio.")
    if not date_clean:
        raise ValueError("Data appello obbligatoria.")
    with get_connection() as conn:
        student = _fetch_student(conn, student_clean)
        if not student:
            raise ValueError("Studente non trovato.")
        exam = _fetch_exam(conn, course_clean, date_clean)
        if not exam:
            raise ValueError("Appello non trovato.")
        duplicate = conn.execute(
            "SELECT id FROM registrations WHERE student_id = ? AND exam_id = ?",
            (student["id"], exam["id"]),
        ).fetchone()
        if duplicate:
            raise ValueError("Studente già iscritto a questo appello.")
        cur = conn.execute(
            "INSERT INTO registrations (student_id, exam_id) VALUES (?, ?)",
            (student["id"], exam["id"]),
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "student_id": student["id"],
            "exam_id": exam["id"],
            "stato": "iscritto",
        }


def record_grade(
    student_matricola: str,
    course_codice: str,
    data_appello: str,
    voto: int,
    lode: bool = False,
) -> dict:
    student_clean = student_matricola.strip()
    course_clean = course_codice.strip()
    date_clean = data_appello.strip()
    if voto not in VALID_VOTO_RANGE:
        raise ValueError("Il voto deve essere compreso tra 18 e 31.")
    if lode and voto != 31:
        raise ValueError("La lode è consentita solo con voto pari a 31.")
    with get_connection() as conn:
        student = _fetch_student(conn, student_clean)
        if not student:
            raise ValueError("Studente non trovato.")
        exam = _fetch_exam(conn, course_clean, date_clean)
        if not exam:
            raise ValueError("Appello non trovato.")
        registration = conn.execute(
            "SELECT * FROM registrations WHERE student_id = ? AND exam_id = ?",
            (student["id"], exam["id"]),
        ).fetchone()
        if not registration:
            raise ValueError("Studente non iscritto all'esame.")
        conn.execute(
            "UPDATE registrations SET voto = ?, lode = ?, stato = ? WHERE id = ?",
            (voto, int(lode), "verbalizzato", registration["id"]),
        )
        conn.commit()
    return get_transcript(student_clean)


def get_transcript(student_matricola: str) -> dict:
    student_clean = student_matricola.strip()
    if not student_clean:
        raise ValueError("Matricola obbligatoria.")
    with get_connection() as conn:
        student = _fetch_student(conn, student_clean)
        if not student:
            raise ValueError("Studente non trovato.")
        rows = conn.execute(
            "SELECT registrations.id, courses.nome AS course_nome, courses.codice AS course_codice, "
            "courses.cfu, exams.data_appello, registrations.voto, registrations.lode, registrations.stato "
            "FROM registrations "
            "JOIN exams ON registrations.exam_id = exams.id "
            "JOIN courses ON exams.course_id = courses.id "
            "WHERE registrations.student_id = ? "
            "ORDER BY exams.data_appello",
            (student["id"],),
        ).fetchall()
        exams_info: List[Dict[str, object]] = []
        total_cfu = 0
        graded_scores: List[int] = []
        for row in rows:
            record = {
                "registration_id": row["id"],
                "course": row["course_nome"],
                "course_codice": row["course_codice"],
                "data_appello": row["data_appello"],
                "voto": row["voto"],
                "lode": bool(row["lode"]),
                "stato": row["stato"],
                "cfu": row["cfu"],
            }
            exams_info.append(record)
            if row["voto"] is not None:
                graded_scores.append(row["voto"])
                if row["stato"] == "verbalizzato":
                    total_cfu += row["cfu"]
        average = round(sum(graded_scores) / len(graded_scores), 2) if graded_scores else None
        return {
            "student": {
                "id": student["id"],
                "matricola": student["matricola"],
                "nome": student["nome"],
                "cognome": student["cognome"],
            },
            "exams": exams_info,
            "average": average,
            "total_cfu": total_cfu,
        }


def delete_registration(student_matricola: str, course_codice: str, data_appello: str) -> None:
    student_clean = student_matricola.strip()
    course_clean = course_codice.strip()
    date_clean = data_appello.strip()
    if not student_clean or not course_clean or not date_clean:
        raise ValueError("Matricola, codice corso e data appello sono obbligatori.")
    with get_connection() as conn:
        student = _fetch_student(conn, student_clean)
        exam = _fetch_exam(conn, course_clean, date_clean)
        if not student or not exam:
            raise ValueError("Registration not found.")
        cur = conn.execute(
            "DELETE FROM registrations WHERE student_id = ? AND exam_id = ?",
            (student["id"], exam["id"]),
        )
        if cur.rowcount == 0:
            raise ValueError("Registration not found.")
        conn.commit()


def delete_grade(student_matricola: str, course_codice: str, data_appello: str) -> dict:
    student_clean = student_matricola.strip()
    course_clean = course_codice.strip()
    date_clean = data_appello.strip()
    if not student_clean or not course_clean or not date_clean:
        raise ValueError("Matricola, codice corso e data appello sono obbligatori.")
    with get_connection() as conn:
        student = _fetch_student(conn, student_clean)
        exam = _fetch_exam(conn, course_clean, date_clean)
        if not student or not exam:
            raise ValueError("Registration not found.")
        registration = conn.execute(
            "SELECT id FROM registrations WHERE student_id = ? AND exam_id = ?",
            (student["id"], exam["id"]),
        ).fetchone()
        if not registration:
            raise ValueError("Registration not found.")
        conn.execute(
            "UPDATE registrations SET voto = NULL, lode = 0, stato = 'iscritto' WHERE id = ?",
            (registration["id"],),
        )
        conn.commit()
    return get_transcript(student_clean)


def list_registrations() -> List[Dict[str, object]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT registrations.id, students.matricola, students.nome, students.cognome, "
            "courses.codice AS course_codice, courses.nome AS course_nome, "
            "exams.data_appello, registrations.stato "
            "FROM registrations "
            "JOIN students ON registrations.student_id = students.id "
            "JOIN exams ON registrations.exam_id = exams.id "
            "JOIN courses ON exams.course_id = courses.id "
            "ORDER BY exams.data_appello"
        ).fetchall()
        return [
            {
                "registration_id": row["id"],
                "matricola": row["matricola"],
                "studente": f"{row['nome']} {row['cognome']}",
                "course_codice": row["course_codice"],
                "course_nome": row["course_nome"],
                "data_appello": row["data_appello"],
                "stato": row["stato"],
            }
            for row in rows
        ]
