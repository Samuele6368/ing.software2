from __future__ import annotations

from typing import List, Optional

#importiamo la libreria per connettersi al database
from db.database import get_connection

#Funzione per la creazione dei corsi nel database
def create_course(codice: str, nome: str, cfu: int) -> dict:

    #sanificazione dei dati in input
    codice_clean = codice.strip()
    nome_clean = nome.strip()

    #validazione dei dati in input
    if not codice_clean:
        raise ValueError("Codice corso obbligatorio.")
    if not nome_clean:
        raise ValueError("Nome corso obbligatorio.")
    if cfu <= 0: #i CFU devono essere maggiori di zero
        raise ValueError("I CFU devono essere maggiori di zero.")

    #apertura della connessione al database
    #"with" apre e chiude automaticamente la connessione
    with get_connection() as conn:

        #query di lettura per per controllare se il codice del corso è già esistente
        #il placeholder "?" viene inserito per indicare che quel valore deve essere letto come testo e non come comando SQL
        exists = conn.execute("SELECT id FROM courses WHERE codice = ?", (codice_clean,)).fetchone()

        #se il corso è già esistente, viene lanciato un errore
        if exists:
            raise ValueError("Codice corso già esistente.")

        #i dati validati e sanificati vengono inseriti nella tabella "courses" del database
        cur = conn.execute(
            "INSERT INTO courses (codice, nome, cfu) VALUES (?, ?, ?)",
            (codice_clean, nome_clean, cfu),
        )

        #le modifiche vengono salvate nel database
        #prima di eseguire "commit" ogni modifica è temporanea
        conn.commit()

        #viene restituito un dizionario con i dati del corso appena creato
        return {
            "id": cur.lastrowid,
            "codice": codice_clean,
            "nome": nome_clean,
            "cfu": cfu,
        }

#Funzione per elencare tutti i corsi presenti nel database
def list_courses() -> List[dict]:

    #Vengono recuperati tutti i corsi ordinati per nome
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM courses ORDER BY nome").fetchall()
        return [dict(row) for row in rows]

#Funzione per recuperare un corso specifico tramite il suo codice
def get_course_by_codice(codice: str) -> Optional[dict]:
    codice_clean = codice.strip()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM courses WHERE codice = ?", (codice_clean,)).fetchone()
        return dict(row) if row else None

#Funzione per eliminare un corso tramite il suo codice
def delete_course(codice: str) -> None:
    codice_clean = codice.strip()
    if not codice_clean:
        raise ValueError("Codice corso obbligatorio.")
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM courses WHERE codice = ?", (codice_clean,))
        if cur.rowcount == 0:
            raise ValueError("Course not found.")
        conn.commit()
