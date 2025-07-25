import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path(__file__).parent / "backend.db"

import secrets

# Ensure database tables exist
def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                company_name TEXT,
                last_sync TEXT,
                last_tally_access TEXT,
                token TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                voucher_data TEXT NOT NULL,
                data_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                missing_fields TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(client_id)
            )
            """
        )
        # Store uploaded voucher details for invoice generation
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vouchers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                voucher_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(client_id)
            )
            """
        )
    return conn

# Simple helper to upsert a client
def upsert_client(
    conn: sqlite3.Connection, client_id: str, company_name: Optional[str] = None
) -> str:
    with conn:
        cur = conn.execute(
            "SELECT token FROM clients WHERE client_id=?", (client_id,)
        )
        row = cur.fetchone()
        if row:
            if company_name:
                conn.execute(
                    "UPDATE clients SET company_name=? WHERE client_id=?",
                    (company_name, client_id),
                )
            return row["token"]
        else:
            token = secrets.token_hex(16)
            conn.execute(
                "INSERT INTO clients (client_id, company_name, token) VALUES (?, ?, ?)",
                (client_id, company_name, token),
            )
            return token

def update_sync(conn: sqlite3.Connection, client_id: str, last_sync: str, tally_access_ok: bool) -> None:
    with conn:
        conn.execute(
            "UPDATE clients SET last_sync=? WHERE client_id=?",
            (last_sync, client_id),
        )
        if tally_access_ok:
            conn.execute(
                "UPDATE clients SET last_tally_access=? WHERE client_id=?",
                (last_sync, client_id),
            )

def get_client_by_token(conn: sqlite3.Connection, token: str) -> Optional[sqlite3.Row]:
    cur = conn.execute(
        "SELECT client_id, token FROM clients WHERE token=?",
        (token,),
    )
    return cur.fetchone()

def get_clients(conn: sqlite3.Connection):
    cur = conn.execute(
        "SELECT client_id, company_name, last_sync, last_tally_access FROM clients ORDER BY client_id"
    )
    return cur.fetchall()

def get_pending_tasks(conn: sqlite3.Connection, client_id: str):
    cur = conn.execute(
        """
        SELECT id, client_id, voucher_data, data_type, created_at
        FROM tasks
        WHERE status='pending' AND client_id=?
        ORDER BY created_at
        """,
        (client_id,),
    )
    return cur.fetchall()

def add_task(conn: sqlite3.Connection, client_id: str, voucher_data: str, data_type: str, status: str = "pending", missing_fields: Optional[str] = None) -> int:
    with conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (client_id, voucher_data, data_type, status, missing_fields)
            VALUES (?, ?, ?, ?, ?)
            """,
            (client_id, voucher_data, data_type, status, missing_fields),
        )
        return cur.lastrowid

def add_voucher(conn: sqlite3.Connection, client_id: str, voucher_data: str) -> int:
    """Insert a voucher record for invoice generation"""
    with conn:
        cur = conn.execute(
            "INSERT INTO vouchers (client_id, voucher_data) VALUES (?, ?)",
            (client_id, voucher_data),
        )
        return cur.lastrowid

def get_voucher(conn: sqlite3.Connection, voucher_id: int) -> Optional[sqlite3.Row]:
    cur = conn.execute(
        "SELECT id, client_id, voucher_data, created_at FROM vouchers WHERE id=?",
        (voucher_id,),
    )
    return cur.fetchone()

def get_rejected_tasks(conn: sqlite3.Connection):
    cur = conn.execute(
        "SELECT client_id, missing_fields FROM tasks WHERE status='rejected'"
    )
    return cur.fetchall()
