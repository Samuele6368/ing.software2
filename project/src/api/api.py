from __future__ import annotations #abilita la sintassi moderna anche per versioni più datate di python

from services import course_service, exam_service, registration_service, student_service


def add_student(matricola: str, nome: str, cognome: str) -> dict:
    return student_service.create_student(matricola, nome, cognome)


def edit_student(matricola: str, nome: str, cognome: str) -> dict:
    return student_service.update_student(matricola, nome, cognome)


def remove_student(matricola: str) -> None:
    student_service.delete_student(matricola)


def list_students() -> list[dict]:
    return student_service.list_students()


def add_course(codice: str, nome: str, cfu: int) -> dict:
    return course_service.create_course(codice, nome, cfu)


def list_courses() -> list[dict]:
    return course_service.list_courses()


def remove_course(codice: str) -> None:
    course_service.delete_course(codice)


def create_exam(course_codice: str, data_appello: str) -> dict:
    return exam_service.create_exam(course_codice, data_appello)


def list_exams(course_codice: str | None = None) -> list[dict]:
    return exam_service.list_exams(course_codice)


def remove_exam(course_codice: str, data_appello: str) -> None:
    exam_service.delete_exam(course_codice, data_appello)


def enroll_student(student_matricola: str, course_codice: str, data_appello: str) -> dict:
    return registration_service.enroll_student(student_matricola, course_codice, data_appello)


def list_registrations() -> list[dict]:
    return registration_service.list_registrations()


def remove_enrollment(student_matricola: str, course_codice: str, data_appello: str) -> None:
    registration_service.delete_registration(student_matricola, course_codice, data_appello)


def record_grade(student_matricola: str, course_codice: str, data_appello: str, voto: int, lode: bool = False) -> dict:
    return registration_service.record_grade(student_matricola, course_codice, data_appello, voto, lode)


def reset_grade(student_matricola: str, course_codice: str, data_appello: str) -> dict:
    return registration_service.delete_grade(student_matricola, course_codice, data_appello)


def get_transcript(student_matricola: str) -> dict:
    return registration_service.get_transcript(student_matricola)
