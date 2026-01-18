from __future__ import annotations

from typing import List, Optional

from db.database import get_connection

#Funzione per sanificare l'input
def _sanitize(text: str) -> str:
    return text.strip()

#Funzione per validare il formato della matricola
def _validate_matricola_format(matricola: str) -> None:
    """Valida che la matricola contenga solo cifre e rappresenti un intero positivo."""
    matricola_stripped = matricola.strip()
    #controlla che la matricola non sia vuota dopo aver rimosso gli spazi
    if not matricola_stripped:
        raise ValueError("Formato non valido: la matricola deve essere un numero intero.")
    #controlla se la matricola contiene solo cifre
    if not matricola_stripped.isdigit():
        raise ValueError("Formato non valido: la matricola deve essere un numero intero.")
    #controlla se la matricola rappresenta un intero positivo
    if int(matricola_stripped) <= 0:
        raise ValueError("Formato non valido: la matricola deve essere un numero intero.")

#Funzione per validare i campi dello studente (matricola, nome, cognome)
def _validate_student_fields(matricola: str, nome: str, cognome: str) -> None:
    _validate_matricola_format(matricola)
    if not nome.strip():
        raise ValueError("Nome obbligatorio.")
    if not cognome.strip():
        raise ValueError("Cognome obbligatorio.")

#Funzione per inserire un nuovo studente nel database
def create_student(matricola: str, nome: str, cognome: str) -> dict:
    #sanificazione dei campi
    _validate_student_fields(matricola, nome, cognome)
    matricola_clean = _sanitize(matricola)
    nome_clean = _sanitize(nome)
    cognome_clean = _sanitize(cognome)
    
    with get_connection() as conn:
        #controlla se la matricola esiste già nel database
        exists = conn.execute("SELECT id FROM students WHERE matricola = ?", (matricola_clean,)).fetchone() #controlla se la matricola esiste già
        if exists:
            raise ValueError("Matricola già esistente.")

        #inserisce il nuovo studente nel database
        cur = conn.execute(
            "INSERT INTO students (matricola, nome, cognome) VALUES (?, ?, ?)", #esegue l'inserimento del dato nel database
            (matricola_clean, nome_clean, cognome_clean),
        )
    #conferma le modifiche e ritorna i dati dello studente creato
        conn.commit()
        return {
            "id": cur.lastrowid,
            "matricola": matricola_clean,
            "nome": nome_clean,
            "cognome": cognome_clean,
        }


    #Funzione per ottenere i dati di uno studente tramite la matricola
def get_student_by_matricola(matricola: str) -> Optional[dict]:
    matricola_clean = _sanitize(matricola)
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM students WHERE matricola = ?", (matricola_clean,)).fetchone()
        return dict(row) if row else None

#funzione per aggiornare i dati di uno studente
def update_student(matricola: str, nome: str, cognome: str) -> dict:
    _validate_student_fields(matricola, nome, cognome)
    matricola_clean = _sanitize(matricola)
    nome_clean = _sanitize(nome)
    cognome_clean = _sanitize(cognome)
    with get_connection() as conn:

        #aggiorna i dati dello studente nel database filtrando per matricola
        cur = conn.execute(
            "UPDATE students SET nome = ?, cognome = ? WHERE matricola = ?",
            (nome_clean, cognome_clean, matricola_clean),
        )

        #cur.row conta quante righe sono state modificate, se è 0 significa che la matricola non esiste
        if cur.rowcount == 0:
            raise ValueError("Studente non trovato.")
        conn.commit()

    #restituisce i dati aggiornati dello studente
    updated = get_student_by_matricola(matricola_clean)
    if not updated:
        raise ValueError("Studente non trovato dopo l'aggiornamento.")
    return updated

#Funzione per eliminare uno studente tramite la matricola
def delete_student(matricola: str) -> None:
    matricola_clean = _sanitize(matricola)
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM students WHERE matricola = ?", (matricola_clean,))
        if cur.rowcount == 0:
            raise ValueError("Student not found.")
        conn.commit()

#Funzione per elencare tutti gli studenti nel database in ordine alfabetico
def list_students() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY cognome, nome").fetchall()
        return [dict(row) for row in rows]