"""
db.py — Database setup and connection management.
All schema creation lives here. Each tree seeds its own data via trees/*.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "life_rpg.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    # ── Trees ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS trees (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,   -- e.g. 'health'
            display     TEXT    NOT NULL,           -- e.g. 'Health'
            level       INTEGER NOT NULL DEFAULT 1,
            xp          INTEGER NOT NULL DEFAULT 0,
            xp_per_lvl  INTEGER NOT NULL DEFAULT 100
        )
    """)

    # ── Objectives ─────────────────────────────────────────────────────────
    # An objective belongs to a tree and optionally a parent objective (branches)
    c.execute("""
        CREATE TABLE IF NOT EXISTS objectives (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tree_id     INTEGER NOT NULL REFERENCES trees(id),
            parent_id   INTEGER REFERENCES objectives(id),
            title       TEXT    NOT NULL,
            description TEXT,
            xp_reward   INTEGER NOT NULL DEFAULT 20,
            completed   INTEGER NOT NULL DEFAULT 0,  -- 0/1 boolean
            sort_order  INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── Gym log ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS gym_log (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            date    TEXT NOT NULL UNIQUE   -- ISO date: YYYY-MM-DD
        )
    """)

    # ── Meditation log ─────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS meditation_types (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            description TEXT,
            summary     TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS meditation_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,           -- ISO date
            type_id     INTEGER NOT NULL REFERENCES meditation_types(id),
            duration    INTEGER NOT NULL DEFAULT 10, -- minutes
            notes       TEXT
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at: {DB_PATH}")