import sqlite3
import json
from datetime import datetime
from typing import Optional, Any

DB_PATH = "pomotracker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            state TEXT NOT NULL,
            pomo_cycles INTEGER NOT NULL,
            remaining_time INTEGER NOT NULL,
            borrow_mode INTEGER NOT NULL,
            work_debt TEXT,
            is_active INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_session(session_data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO sessions (start_time, last_updated, state, pomo_cycles, remaining_time, borrow_mode, work_debt, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            now,
            session_data["state"],
            session_data["pomo_cycles"],
            session_data["remaining_time"],
            session_data["borrow_mode"],
            json.dumps(session_data["work_debt"]),
            1,
        ),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def update_session(session_id: int, session_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE sessions
        SET last_updated = ?, state = ?, pomo_cycles = ?, remaining_time = ?, borrow_mode = ?, work_debt = ?
        WHERE id = ?
        """,
        (
            datetime.now().isoformat(),
            session_data["state"],
            session_data["pomo_cycles"],
            session_data["remaining_time"],
            session_data["borrow_mode"],
            json.dumps(session_data["work_debt"]),
            session_id,
        ),
    )
    conn.commit()
    conn.close()

def get_active_session() -> Optional[sqlite3.Row]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE is_active = 1 ORDER BY last_updated DESC LIMIT 1")
    session = cursor.fetchone()
    conn.close()
    return session

def deactivate_session(session_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def deactivate_all_sessions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET is_active = 0")
    conn.commit()
    conn.close()
