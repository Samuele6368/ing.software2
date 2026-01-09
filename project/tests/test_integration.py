from __future__ import annotations

from api import api


def test_full_enrollment_and_grading_flow(tmp_db):
    api.add_course("INF01", "Informatica", 6)
    api.create_exam("INF01", "2025-01-15")
    api.add_student("999", "Anna", "Bianchi")
    api.enroll_student("999", "INF01", "2025-01-15")
    api.record_grade("999", "INF01", "2025-01-15", 30, False)

    transcript = api.get_transcript("999")
    assert transcript["average"] == 30
    assert transcript["total_cfu"] == 6
    assert transcript["exams"][0]["stato"] == "verbalizzato"


def test_delete_course_cascades_registrations(tmp_db):
    api.add_course("MAT01", "Analisi", 12)
    api.create_exam("MAT01", "2025-03-01")
    api.add_student("200", "Luca", "Verdi")
    api.enroll_student("200", "MAT01", "2025-03-01")

    api.remove_course("MAT01")

    assert api.list_courses() == []
    assert api.list_exams() == []
    transcript = api.get_transcript("200")
    assert transcript["exams"] == []


def test_delete_exam_removes_registrations(tmp_db):
    api.add_course("FIS01", "Fisica", 8)
    api.create_exam("FIS01", "2025-04-20")
    api.add_student("300", "Giulia", "Neri")
    api.enroll_student("300", "FIS01", "2025-04-20")

    api.remove_exam("FIS01", "2025-04-20")

    assert api.list_exams() == []
    transcript = api.get_transcript("300")
    assert transcript["exams"] == []


def test_delete_grade_resets_values(tmp_db):
    api.add_course("CHM01", "Chimica", 6)
    api.create_exam("CHM01", "2025-05-15")
    api.add_student("400", "Marta", "Blu")
    api.enroll_student("400", "CHM01", "2025-05-15")
    api.record_grade("400", "CHM01", "2025-05-15", 30, False)

    api.reset_grade("400", "CHM01", "2025-05-15")

    transcript = api.get_transcript("400")
    assert transcript["exams"][0]["voto"] is None
    assert transcript["exams"][0]["stato"] == "iscritto"
