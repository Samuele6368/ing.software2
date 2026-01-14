from __future__ import annotations #abilita la sintassi moderna anche per versioni più datate di python

from services import course_service, exam_service, registration_service, student_service #import dei servizi necessari

#funzione per aggiungere uno studente
def add_student(matricola: str, nome: str, cognome: str) -> dict:
    return student_service.create_student(matricola, nome, cognome)

#funzione per modificare uno studente
def edit_student(matricola: str, nome: str, cognome: str) -> dict:
    return student_service.update_student(matricola, nome, cognome)

#funzione per rimuovere uno studente
def remove_student(matricola: str) -> None:
    student_service.delete_student(matricola)

#funzione per elencare tutti gli studenti
def list_students() -> list[dict]:
    return student_service.list_students()

#funzione per aggiungere un corso
def add_course(codice: str, nome: str, cfu: int) -> dict:
    return course_service.create_course(codice, nome, cfu)

#funzione per elencare tutti i corsi
def list_courses() -> list[dict]:
    return course_service.list_courses()

#funzione per rimuovere un corso
def remove_course(codice: str) -> None:
    course_service.delete_course(codice)

#funzione per creare un appello d'esame
def create_exam(course_codice: str, data_appello: str) -> dict:
    return exam_service.create_exam(course_codice, data_appello)

#funzione per elencare gli appelli d'esame
def list_exams(course_codice: str | None = None) -> list[dict]:
    return exam_service.list_exams(course_codice)

#funzione per rimuovere un appello d'esame
def remove_exam(course_codice: str, data_appello: str) -> None:
    exam_service.delete_exam(course_codice, data_appello)

#funzione per iscrivere uno studente a un appello d'esame
def enroll_student(student_matricola: str, course_codice: str, data_appello: str) -> dict:
    return registration_service.enroll_student(student_matricola, course_codice, data_appello)

#funzione per elencare tutte le iscrizioni
def list_registrations() -> list[dict]:
    return registration_service.list_registrations()

#funzione per rimuovere un'iscrizione
def remove_enrollment(student_matricola: str, course_codice: str, data_appello: str) -> None:
    registration_service.delete_registration(student_matricola, course_codice, data_appello)

#funzione per registrare un voto
def record_grade(student_matricola: str, course_codice: str, data_appello: str, voto: int, lode: bool = False) -> dict:
    return registration_service.record_grade(student_matricola, course_codice, data_appello, voto, lode)

#funzione per resettare un voto
def reset_grade(student_matricola: str, course_codice: str, data_appello: str) -> dict:
    return registration_service.delete_grade(student_matricola, course_codice, data_appello)

#funzione per ottenere il transcript di uno studente
def get_transcript(student_matricola: str) -> dict:
    return registration_service.get_transcript(student_matricola)
