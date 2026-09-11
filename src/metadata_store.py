"""SQLite storage for photo file metadata, keyed by absolute path."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    file_hash TEXT NOT NULL,
    mtime REAL NOT NULL,
    width INTEGER,
    height INTEGER,
    taken_at TEXT
);
"""


class MetadataStore:
    def __init__(self, db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False: Streamlit's cached resource is reused across
        # the per-session script-runner threads that call into this store.
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def get_by_path(self, path):
        cur = self.conn.execute(
            "SELECT id, file_hash, mtime FROM photos WHERE path = ?", (path,)
        )
        return cur.fetchone()

    def upsert(self, path, file_hash, mtime, width, height, taken_at):
        self.conn.execute(
            """INSERT INTO photos (path, file_hash, mtime, width, height, taken_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(path) DO UPDATE SET
                 file_hash=excluded.file_hash, mtime=excluded.mtime,
                 width=excluded.width, height=excluded.height, taken_at=excluded.taken_at
            """,
            (path, file_hash, mtime, width, height, taken_at),
        )
        self.conn.commit()
        return self.get_by_path(path)[0]

    def get_path_by_id(self, photo_id):
        row = self.conn.execute(
            "SELECT path FROM photos WHERE id = ?", (photo_id,)
        ).fetchone()
        return row[0] if row else None

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM photos").fetchone()[0]

    def all_paths(self):
        return [r[0] for r in self.conn.execute("SELECT path FROM photos")]

    def close(self):
        self.conn.close()
