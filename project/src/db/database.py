from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Union

SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SRC_DIR.parent
MIGRATIONS_PATH = Path(__file__).resolve().parent / "migrations.sql"
DEFAULT_DB_PATH = PROJECT_ROOT / "student_exam_manager.db"

_DB_PATH = DEFAULT_DB_PATH


def _coerce_path(value: Union[Path, str]) -> Path:
    return value if isinstance(value, Path) else Path(value)


def _set_db_path(db_path: Union[Path, str]) -> Path:
    global _DB_PATH
    _DB_PATH = _coerce_path(db_path)
    return _DB_PATH


def _resolved_path(db_path: Optional[Union[Path, str]]) -> Path:
    if db_path is not None:
        return _coerce_path(db_path)
    return _DB_PATH


def get_connection(db_path: Optional[Union[Path, str]] = None) -> sqlite3.Connection:
    path = _resolved_path(db_path) #trova il percorso del database in automatico (rende il software portable)
    path.parent.mkdir(parents=True, exist_ok=True) #crea la cartella del database se non esiste ed in caso la crea
    conn = sqlite3.connect(path) #apre la connessione al database
    conn.row_factory = sqlite3.Row #imposta la modalità di accesso alle righe del database come dizionari invece che con numeri
    return conn


def init_db(db_path: Optional[Union[Path, str]] = None) -> Path:
    target_path = _resolved_path(db_path)
    if db_path is not None:
        _set_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    script = MIGRATIONS_PATH.read_text(encoding="utf-8") #legge il file di migrazione
    with get_connection(target_path) as conn:
        conn.executescript(script) #esegue lo script di migrazione per creare le tabelle da SQlite
    return target_path


def reset_db(db_path: Optional[Union[Path, str]] = None) -> Path:
    target_path = _resolved_path(db_path)
    if db_path is not None:
        _set_db_path(db_path)
    if target_path.exists():
        target_path.unlink()
    return init_db(target_path)
