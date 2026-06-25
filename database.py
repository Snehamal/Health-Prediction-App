"""
database.py
------------
Handles all SQLite persistence for patient records.

Why SQLite?
- Zero setup: it's just a local file (health_app.db), no server process,
  no Docker, no separate install. Perfect for a take-home task and for
  the reviewer to run instantly on their own machine.
- Still fully relational/SQL, so the schema and query logic shown here
  would translate directly to PostgreSQL/MySQL if this were scaled up.

All functions here are plain, explicit SQL via the built-in `sqlite3`
module (no ORM) so the logic is easy to read and explain in an interview.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "health_app.db")


def get_connection():
    """Create a new database connection. `row_factory` lets us fetch rows as dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the patients table if it doesn't already exist."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        email TEXT NOT NULL,
        glucose REAL NOT NULL,
        haemoglobin REAL NOT NULL,
        cholesterol REAL NOT NULL,
        remarks TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """
    conn = get_connection()
    try:
        conn.execute(create_sql)
        conn.commit()
    finally:
        conn.close()


def create_patient(full_name, dob, email, glucose, haemoglobin, cholesterol, remarks):
    """Insert a new patient record. Returns the new record's id."""
    sql = """
    INSERT INTO patients
        (full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    conn = get_connection()
    try:
        cur = conn.execute(sql, (full_name, str(dob), email, glucose, haemoglobin, cholesterol, remarks))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_all_patients():
    """Return all patient records as a list of dicts, newest first."""
    sql = "SELECT * FROM patients ORDER BY id DESC;"
    conn = get_connection()
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_patient_by_id(patient_id):
    sql = "SELECT * FROM patients WHERE id = ?;"
    conn = get_connection()
    try:
        row = conn.execute(sql, (patient_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_patient(patient_id, full_name, dob, email, glucose, haemoglobin, cholesterol, remarks):
    """Update an existing patient record by id."""
    sql = """
    UPDATE patients
    SET full_name = ?,
        date_of_birth = ?,
        email = ?,
        glucose = ?,
        haemoglobin = ?,
        cholesterol = ?,
        remarks = ?
    WHERE id = ?;
    """
    conn = get_connection()
    try:
        conn.execute(sql, (full_name, str(dob), email, glucose, haemoglobin, cholesterol, remarks, patient_id))
        conn.commit()
    finally:
        conn.close()


def delete_patient(patient_id):
    sql = "DELETE FROM patients WHERE id = ?;"
    conn = get_connection()
    try:
        conn.execute(sql, (patient_id,))
        conn.commit()
    finally:
        conn.close()
