#!/usr/bin/env python3
import sqlite3

DB_FILE = "/data/app.db"


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
    cur.execute("""DROP TABLE IF EXISTS tokens;""")

    cur.execute("""
    CREATE TABLE tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        type TEXT NOT NULL CHECK (type IN ('activation', 'password_reset')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cur.execute("CREATE INDEX idx_tokens_user_id ON tokens(user_id);")

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

    # Create an initial user for testing
    create_initial_user(conn)
    print("Initial user created.")
    print("Email: user@domain.org")
    print("Password: Bonjour123!")

    conn.commit()
    conn.close()
    print(f"Database initialized successfully: {DB_FILE}")


def create_initial_user(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO users (id, email, password_hash, created_at, activated)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            1,
            "user@domain.org",
            "scrypt:32768:8:1$0iGmdM53ifrZnXpX$78413db3ee07ba0fd89bcc2cd5ac9b8bcbe75c83eb8021a07be951887fd0848d5f0e711f484f2c8da25c8810fb9eaf7f24085b00a0bad3a6b10e451d1c01c2c6",
            "2025-12-03T13:01:23.267399",
            1,
        ),
    )
    conn.commit()



if __name__ == "__main__":
    init_db()
