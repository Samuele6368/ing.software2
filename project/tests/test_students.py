from __future__ import annotations

import pytest

from api import api


def test_student_crud_flow(tmp_db):
    created = api.add_student("12345", "Mario", "Rossi")
    assert created["matricola"] == "12345"

    students = api.list_students()
    assert any(s["matricola"] == "12345" for s in students)

    api.edit_student("12345", "Luigi", "Verdi")
    updated = next(s for s in api.list_students() if s["matricola"] == "12345")
    assert updated["nome"] == "Luigi"
    assert updated["cognome"] == "Verdi"

    api.remove_student("12345")
    students = api.list_students()
    assert all(s["matricola"] != "12345" for s in students)


def test_delete_student_cascade(tmp_db):
    api.add_course("INF99", "Algoritmi", 9)
    api.create_exam("INF99", "2025-02-10")
    api.add_student("777", "Paolo", "Rossi")
    api.enroll_student("777", "INF99", "2025-02-10")
    api.remove_student("777")

    assert all(s["matricola"] != "777" for s in api.list_students())
    assert all(reg["matricola"] != "777" for reg in api.list_registrations())
    with pytest.raises(ValueError, match="Studente non trovato"):
        api.get_transcript("777")


def test_matricola_validation_valid_integer(tmp_db):
    """Test che una matricola numerica valida venga accettata."""
    created = api.add_student("12345", "Mario", "Rossi")
    assert created["matricola"] == "12345"
    students = api.list_students()
    assert any(s["matricola"] == "12345" for s in students)


def test_matricola_validation_non_numeric_letters(tmp_db):
    """Test che una matricola con lettere venga rifiutata."""
    with pytest.raises(ValueError, match="Formato non valido"):
        api.add_student("ABC", "Mario", "Rossi")


def test_matricola_validation_mixed_alphanumeric(tmp_db):
    """Test che una matricola mista (numeri e lettere) venga rifiutata."""
    with pytest.raises(ValueError, match="Formato non valido"):
        api.add_student("12A34", "Mario", "Rossi")


def test_matricola_validation_empty_string(tmp_db):
    """Test che una matricola vuota venga rifiutata."""
    with pytest.raises(ValueError, match="Formato non valido"):
        api.add_student("", "Mario", "Rossi")


def test_matricola_validation_zero(tmp_db):
    """Test che una matricola con valore zero venga rifiutata."""
    with pytest.raises(ValueError, match="Formato non valido"):
        api.add_student("0", "Mario", "Rossi")


def test_matricola_validation_negative(tmp_db):
    """Test che una matricola negativa venga rifiutata."""
    with pytest.raises(ValueError, match="Formato non valido"):
        api.add_student("-123", "Mario", "Rossi")


def test_matricola_validation_update_student(tmp_db):
    """Test che la validazione della matricola funzioni anche in update_student."""
    # Prima crea uno studente valido
    api.add_student("12345", "Mario", "Rossi")
    # Poi prova ad aggiornare con una matricola non valida (anche se update_student non cambia la matricola,
    # la validazione viene comunque eseguita su quella esistente)
    # In realtà update_student non cambia la matricola, quindi testiamo che la validazione funzioni
    # quando viene passata una matricola non valida come parametro
    with pytest.raises(ValueError, match="Formato non valido"):
        api.edit_student("ABC", "Luigi", "Verdi")