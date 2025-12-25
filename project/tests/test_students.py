from __future__ import annotations

import pytest

from api import api


def test_student_crud_flow(tmp_db):
    created = api.add_student("S123", "Mario", "Rossi")
    assert created["matricola"] == "S123"

    students = api.list_students()
    assert any(s["matricola"] == "S123" for s in students)

    api.edit_student("S123", "Luigi", "Verdi")
    updated = next(s for s in api.list_students() if s["matricola"] == "S123")
    assert updated["nome"] == "Luigi"
    assert updated["cognome"] == "Verdi"

    api.remove_student("S123")
    students = api.list_students()
    assert all(s["matricola"] != "S123" for s in students)


def test_delete_student_cascade(tmp_db):
    api.add_course("INF99", "Algoritmi", 9)
    api.create_exam("INF99", "2025-02-10")
    api.add_student("S777", "Paolo", "Rossi")
    api.enroll_student("S777", "INF99", "2025-02-10")
    api.remove_student("S777")

    assert all(s["matricola"] != "S777" for s in api.list_students())
    assert all(reg["matricola"] != "S777" for reg in api.list_registrations())
    with pytest.raises(ValueError, match="Student not found."):
        api.get_transcript("S777")
