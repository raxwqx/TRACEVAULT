from contextlib import contextmanager
from pathlib import Path
import sqlite3

APP_DIR = Path(__file__).resolve().parent.parent
DB_PATH = APP_DIR / "data" / "tracevault.db"


def _connect():
    """Open a raw SQLite connection.

    Prefer :func:`get_conn`, which also commits, rolls back and closes the
    connection correctly.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def get_conn():
    """Yield a SQLite connection and always close it afterwards.

    ``with sqlite3.connect(...)`` only manages the transaction, it does not
    close the connection. Streamlit keeps the process alive for a long time,
    so leaking file descriptors would eventually break the app.
    """
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as con:
        con.execute("PRAGMA journal_mode = WAL")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Açık',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            url TEXT NOT NULL DEFAULT '',
            source_type TEXT NOT NULL,
            accessed_at TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            details TEXT NOT NULL,
            confidence TEXT NOT NULL,
            source_id INTEGER REFERENCES sources(id) ON DELETE SET NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            event_time_utc TEXT NOT NULL,
            timezone_note TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
            left_node TEXT NOT NULL,
            right_node TEXT NOT NULL,
            label TEXT NOT NULL DEFAULT 'ilişkili',
            created_at TEXT NOT NULL,
            UNIQUE(case_id, left_node, right_node, label)
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            folder TEXT NOT NULL DEFAULT 'Gelen Kutusu',
            tags TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id);
        CREATE INDEX IF NOT EXISTS idx_sources_case ON sources(case_id);
        CREATE INDEX IF NOT EXISTS idx_findings_case ON findings(case_id);
        CREATE INDEX IF NOT EXISTS idx_events_case_time ON events(case_id, event_time_utc);
        CREATE INDEX IF NOT EXISTS idx_relationships_case ON relationships(case_id);
        CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated_at DESC);
        """)
