"""
trees/health.py — Seeds the health tree with objectives and meditation types.
Run once on first launch via main.py → db.init_db() → seed_all_trees().
"""

from db import get_connection


MEDITATION_TYPES = [
    {
        "name": "Mindfulness",
        "description": "Focused awareness of the present moment — breath, body, sensations.",
        "summary": (
            "Mindfulness meditation trains you to observe thoughts without judgement. "
            "Sit comfortably, close your eyes, and follow your breath. When your mind "
            "wanders — and it will — gently return focus to the breath. Even 5–10 minutes "
            "daily rewires stress-response pathways over weeks."
        ),
    },
    {
        "name": "Visualisation",
        "description": "Mental rehearsal of goals, performance, or desired future states.",
        "summary": (
            "Used by elite athletes and high performers. Close your eyes and vividly imagine "
            "achieving a specific goal — engage all senses. Feel the emotion of success. "
            "This primes your reticular activating system to notice opportunities and "
            "builds neural pathways associated with the desired behaviour."
        ),
    },
    {
        "name": "Box Breathing",
        "description": "4-4-4-4 breath pattern used by Navy SEALs to control stress response.",
        "summary": (
            "Inhale for 4 counts → hold for 4 → exhale for 4 → hold for 4. Repeat for "
            "4–8 minutes. Activates the parasympathetic nervous system, lowers cortisol, "
            "and sharpens focus. Ideal before high-pressure situations or to reset "
            "mid-day stress."
        ),
    },
    {
        "name": "Body Scan",
        "description": "Progressive relaxation moving attention through each part of the body.",
        "summary": (
            "Lie down or sit. Starting from the crown of your head, slowly move attention "
            "down through your face, neck, shoulders, arms, chest, abdomen, legs, and feet. "
            "Notice tension without trying to fix it — awareness alone begins to release it. "
            "Excellent for sleep preparation and chronic tension relief."
        ),
    },
    {
        "name": "Gratitude",
        "description": "Deliberately cultivating appreciation for what is already good.",
        "summary": (
            "Close your eyes and bring to mind 3 specific things you're genuinely grateful "
            "for today — be concrete, not generic. Sit with the feeling each one produces. "
            "Research shows consistent gratitude practice increases baseline happiness, "
            "reduces anxiety, and improves sleep quality over 4–8 weeks."
        ),
    },
]


OBJECTIVES = [
    # ── Level 1 — Building the habit ────────────────────────────────────────
    {"title": "First week at the gym", "description": "Log 3 gym sessions in your first week.", "xp": 30, "parent": None, "sort": 1},
    {"title": "First meditation", "description": "Complete your first logged meditation session.", "xp": 15, "parent": None, "sort": 2},
    {"title": "Morning routine established", "description": "Log gym or meditation for 7 consecutive days.", "xp": 40, "parent": None, "sort": 3},

    # ── Level 2 — Consistency ───────────────────────────────────────────────
    {"title": "30-day gym streak", "description": "Hit the gym at least 3x per week for a full month.", "xp": 80, "parent": None, "sort": 4},
    {"title": "Meditation variety", "description": "Try all 5 meditation types at least once.", "xp": 50, "parent": None, "sort": 5},
    {"title": "10-session milestone", "description": "Log 10 total meditation sessions.", "xp": 40, "parent": None, "sort": 6},

    # ── Level 3 — Mastery ───────────────────────────────────────────────────
    {"title": "100 gym sessions", "description": "Log 100 total gym sessions — you've made this a lifestyle.", "xp": 150, "parent": None, "sort": 7},
    {"title": "Daily meditator", "description": "Log meditation every day for 30 consecutive days.", "xp": 100, "parent": None, "sort": 8},
    {"title": "Mind-body integration", "description": "Complete both gym and meditation on the same day, 10 times.", "xp": 80, "parent": None, "sort": 9},
]


def seed(conn=None):
    """Insert health tree + its objectives and meditation types if not present."""
    close = conn is None
    if close:
        conn = get_connection()
    c = conn.cursor()

    # Upsert the tree
    c.execute("""
        INSERT INTO trees (name, display, xp_per_lvl)
        VALUES ('health', 'Health', 100)
        ON CONFLICT(name) DO NOTHING
    """)

    tree_id = c.execute("SELECT id FROM trees WHERE name='health'").fetchone()["id"]

    # Seed meditation types
    for mt in MEDITATION_TYPES:
        c.execute("""
            INSERT INTO meditation_types (name, description, summary)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO NOTHING
        """, (mt["name"], mt["description"], mt["summary"]))

    # Seed objectives
    existing = c.execute(
        "SELECT COUNT(*) as n FROM objectives WHERE tree_id=?", (tree_id,)
    ).fetchone()["n"]

    if existing == 0:
        for obj in OBJECTIVES:
            c.execute("""
                INSERT INTO objectives (tree_id, parent_id, title, description, xp_reward, sort_order)
                VALUES (?, NULL, ?, ?, ?, ?)
            """, (tree_id, obj["title"], obj["description"], obj["xp"], obj["sort"]))

    conn.commit()
    if close:
        conn.close()