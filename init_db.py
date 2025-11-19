#!/usr/bin/env python3
import sqlite3

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # ================================
    # USERS TABLE
    # ================================
    cur.execute("""DROP TABLE IF EXISTS users;""")

    cur.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        activated INTEGER DEFAULT 0 CHECK (activated IN (0,1))
    );
    """)

    cur.execute("CREATE INDEX idx_users_email ON users(email);")

    # ================================
    # ACTIVATION TOKENS TABLE
    # ================================
    cur.execute("""DROP TABLE IF EXISTS activation_tokens;""")

    cur.execute("""
    CREATE TABLE activation_tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cur.execute("CREATE INDEX idx_tokens_user_id ON activation_tokens(user_id);")

    # ================================
    # OPTIONAL SECURITY EVENTS TABLE
    # Uncomment to enable logs
    # ================================
    """
    cur.execute("DROP TABLE IF EXISTS security_events;")
    cur.execute(\"
    CREATE TABLE security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        user_id INTEGER,
        event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        details TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    \")
    cur.execute("CREATE INDEX idx_events_user_id ON security_events(user_id);")
    """

    conn.commit()
    conn.close()
    print(f"Database initialized successfully: {DB_FILE}")

if __name__ == "__main__":
    init_db()
