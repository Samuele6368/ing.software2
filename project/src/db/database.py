from __future__ import annotations

#Libreria standard per la gestione del database SQLite
import sqlite3

#Libreria standard per la gestione dei percorsi dei file, rende il codice portatile
from pathlib import Path

#Libreria standard per i Type Hints:
#Optional: la variabile può essere "None"
#Union: la variabile può essere di più tipi
from typing import Optional, Union

#Configurazione percorsi:

# __file__ è il percorso del file "database.py"
# .resolve() trova il percorso preciso del file "database.py".
# .parent.parent risale di due cartelle.
SRC_DIR = Path(__file__).resolve().parent.parent

#risale di una cartella per trovare la directory del progetto
PROJECT_ROOT = SRC_DIR.parent

#trova il percorso del file "migrations.sql" che si trova nella stessa cartella del file "database.py",
MIGRATIONS_PATH = Path(__file__).resolve().parent / "migrations.sql"

#imposta il percorso di default del database nella cartella principale del progetto, e imposta il nome del file del database
DEFAULT_DB_PATH = PROJECT_ROOT / "student_exam_manager.db"

#memorizza il percorso del database in uso
_DB_PATH = DEFAULT_DB_PATH

#converte una stringa in un percorso Path se non lo è già
def _coerce_path(value: Union[Path, str]) -> Path:
    return value if isinstance(value, Path) else Path(value)

# Aggiorna la variabile globale per "puntare" a un nuovo file database. 
def _set_db_path(db_path: Union[Path, str]) -> Path:
    global _DB_PATH
    _DB_PATH = _coerce_path(db_path)
    return _DB_PATH

#distinguo 2 casi:
#caso 1: indico un percorso specifico, e allora verrà usato il percorso indicato
#caso 2: non indico nulla e uso il percorso di default
def _resolved_path(db_path: Optional[Union[Path, str]]) -> Path:
    if db_path is not None:
        return _coerce_path(db_path)
    return _DB_PATH

def get_connection(db_path: Optional[Union[Path, str]] = None) -> sqlite3.Connection:
    #trova il percorso del database in automatico
    path = _resolved_path(db_path)
    #crea la cartella del database
    #in caso non esistesse anche la cartella padre, viene creata anche quella (parents=True)
    #se la cartella esiste già, non da errore
    path.parent.mkdir(parents=True, exist_ok=True)
    #viene aperta la connessione al file del database
    conn = sqlite3.connect(path)
    #imposta la modalità di accesso alle righe del database come dizionari invece che con numeri
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[Union[Path, str]] = None) -> Path:
    target_path = _resolved_path(db_path)
    if db_path is not None:
        _set_db_path(db_path)
    #assicuro che la cartella esista
    target_path.parent.mkdir(parents=True, exist_ok=True)
    #legge il file di migrazione
    #encoding="utf-8" serve per assicurarsi che i caratteri speciali vengano letti correttamente
    script = MIGRATIONS_PATH.read_text(encoding="utf-8") 
    #viene aperta la connessione
    with get_connection(target_path) as conn:
        #esegue lo script di migrazione per creare le tabelle da SQlite
        conn.executescript(script) 
    return target_path


def reset_db(db_path: Optional[Union[Path, str]] = None) -> Path:
    target_path = _resolved_path(db_path)
    if db_path is not None:
        _set_db_path(db_path)
    #controllo se il file esista
    if target_path.exists():
        #viene cancellato il file dal file system per eliminare i dati e la struttura delle tabelle
        target_path.unlink()
    return init_db(target_path)