 
import json
import sqlite3
from datetime import datetime
 
DB_PATH = "intake.db"
 
 
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                number          TEXT PRIMARY KEY,   -- 'whatsapp:+1555...'
                profile_name    TEXT,
                state           TEXT NOT NULL,       -- collecting|confirming|under_review|approved
                q_index         INTEGER NOT NULL,    -- which question they're on
                answers         TEXT NOT NULL,       -- JSON: {question_key: answer}
                airtable_id     TEXT,                -- record id once exported
                created_at      TEXT NOT NULL,
                updated_at      TEXT NOT NULL
            )
            """
        )
 
 
def get_conversation(number):
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM conversations WHERE number = ?", (number,)
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["answers"] = json.loads(data["answers"])
        return data
 
 
def start_conversation(number, profile_name):
    """Create a fresh conversation at question 0, state 'collecting'."""
    now = datetime.utcnow().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO conversations "
            "(number, profile_name, state, q_index, answers, airtable_id, created_at, updated_at) "
            "VALUES (?, ?, 'collecting', 0, '{}', NULL, ?, ?)",
            (number, profile_name, now, now),
        )
 
 
def save_answer(number, key, value):
    """Store one answer and advance the question index by 1."""
    convo = get_conversation(number)
    if convo is None:
        raise ValueError(f"No conversation found for {number}")
    convo["answers"][key] = value
    with _conn() as conn:
        conn.execute(
            "UPDATE conversations SET answers = ?, q_index = q_index + 1, updated_at = ? "
            "WHERE number = ?",
            (json.dumps(convo["answers"]), datetime.utcnow().isoformat(), number),
        )
 
 
def set_state(number, state, airtable_id=None):
    with _conn() as conn:
        if airtable_id is not None:
            conn.execute(
                "UPDATE conversations SET state = ?, airtable_id = ?, updated_at = ? "
                "WHERE number = ?",
                (state, airtable_id, datetime.utcnow().isoformat(), number),
            )
        else:
            conn.execute(
                "UPDATE conversations SET state = ?, updated_at = ? WHERE number = ?",
                (state, datetime.utcnow().isoformat(), number),
            )
 