"""
models.py — Data access layer.
Functions that read/write to the database. No UI logic here.
"""

from db import get_connection
from datetime import date


# ── Trees ──────────────────────────────────────────────────────────────────

def get_tree(name: str) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM trees WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_xp(tree_name: str, amount: int) -> dict:
    """
    Add XP to a tree. Handles level-ups automatically.
    Returns the updated tree dict, plus a 'levelled_up' bool.
    """
    conn = get_connection()
    tree = dict(conn.execute("SELECT * FROM trees WHERE name = ?", (tree_name,)).fetchone())
    tree["xp"] += amount
    levelled_up = False

    while tree["xp"] >= tree["xp_per_lvl"]:
        tree["xp"] -= tree["xp_per_lvl"]
        tree["level"] += 1
        tree["xp_per_lvl"] = int(tree["xp_per_lvl"] * 1.2)  # scaling difficulty
        levelled_up = True

    conn.execute(
        "UPDATE trees SET xp=?, level=?, xp_per_lvl=? WHERE name=?",
        (tree["xp"], tree["level"], tree["xp_per_lvl"], tree_name)
    )
    conn.commit()
    conn.close()
    tree["levelled_up"] = levelled_up
    return tree


# ── Objectives ─────────────────────────────────────────────────────────────

def get_objectives(tree_name: str) -> list[dict]:
    conn = get_connection()
    tree = conn.execute("SELECT id FROM trees WHERE name = ?", (tree_name,)).fetchone()
    rows = conn.execute(
        "SELECT * FROM objectives WHERE tree_id = ? ORDER BY sort_order, id",
        (tree["id"],)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def complete_objective(objective_id: int, tree_name: str) -> dict:
    """Mark an objective done and award XP. Returns updated tree."""
    conn = get_connection()
    obj = conn.execute("SELECT * FROM objectives WHERE id = ?", (objective_id,)).fetchone()
    if obj and not obj["completed"]:
        conn.execute("UPDATE objectives SET completed = 1 WHERE id = ?", (objective_id,))
        conn.commit()
    conn.close()
    return add_xp(tree_name, obj["xp_reward"]) if obj else None


def uncomplete_objective(objective_id: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE objectives SET completed = 0 WHERE id = ?", (objective_id,))
    conn.commit()
    conn.close()


# ── Gym log ────────────────────────────────────────────────────────────────

def log_gym(day: str = None) -> bool:
    """Log a gym session. Returns True if new, False if already logged."""
    day = day or date.today().isoformat()
    conn = get_connection()
    try:
        conn.execute("INSERT INTO gym_log (date) VALUES (?)", (day,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False


def remove_gym_log(day: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM gym_log WHERE date = ?", (day,))
    conn.commit()
    conn.close()


def get_gym_logs(year: int, month: int) -> list[str]:
    """Return list of ISO date strings for a given month."""
    conn = get_connection()
    prefix = f"{year:04d}-{month:02d}"
    rows = conn.execute(
        "SELECT date FROM gym_log WHERE date LIKE ? ORDER BY date",
        (f"{prefix}%",)
    ).fetchall()
    conn.close()
    return [r["date"] for r in rows]


def get_gym_streak() -> int:
    """Return current consecutive-day gym streak."""
    conn = get_connection()
    rows = conn.execute("SELECT date FROM gym_log ORDER BY date DESC").fetchall()
    conn.close()
    if not rows:
        return 0
    dates = [date.fromisoformat(r["date"]) for r in rows]
    streak = 0
    check = date.today()
    for d in dates:
        if d == check:
            streak += 1
            check = date(check.year, check.month, check.day - 1) if check.day > 1 else \
                    date(check.year, check.month - 1 if check.month > 1 else 12,
                         [31,28,31,30,31,30,31,31,30,31,30,31][check.month - 2])
        else:
            break
    return streak


# ── Meditation ─────────────────────────────────────────────────────────────

def get_meditation_types() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM meditation_types ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_meditation(type_id: int, duration: int, notes: str = "") -> None:
    day = date.today().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO meditation_log (date, type_id, duration, notes) VALUES (?,?,?,?)",
        (day, type_id, duration, notes)
    )
    conn.commit()
    conn.close()


def get_meditation_logs(limit: int = 30) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT ml.date, ml.duration, ml.notes, mt.name as type_name
        FROM meditation_log ml
        JOIN meditation_types mt ON mt.id = ml.type_id
        ORDER BY ml.date DESC, ml.id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]