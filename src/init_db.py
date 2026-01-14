#!/usr/bin/env python3
import sqlite3
import os

DB_FILE = "/data/app.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = OFF;")
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
        last_login DATETIME,
        nb_failed_logins INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        activated INTEGER DEFAULT 0 CHECK (activated IN (0,1)),
        mfa_enabled INTEGER DEFAULT 0 CHECK (mfa_enabled IN (0,1)),
        mfa_secret TEXT,
        backup_codes TEXT,
        role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user','admin')),
        disabled INTEGER DEFAULT 0 CHECK (disabled IN (0,1)),
        disabled_by_admin INTEGER DEFAULT 0 CHECK (disabled_by_admin IN (0,1))
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
        used INTEGER DEFAULT 0 CHECK (used IN (0,1)),
        user_id INTEGER NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        type TEXT NOT NULL CHECK (type IN ('activation', 'password_reset')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cur.execute("CREATE INDEX idx_tokens_user_id ON tokens(user_id);")

    # ================================
    # POSTS TABLE
    # ================================
    cur.execute("DROP TABLE IF EXISTS posts;")
    cur.execute("""
        CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        is_public INTEGER DEFAULT 1,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (author_id) REFERENCES users(id)
    );
    """)

    # ================================
    # COMMENTS TABLE
    # ================================
    cur.execute("DROP TABLE IF EXISTS comments;")
    cur.execute("""
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users(id),
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );
    """)

    # ================================
    # ATTACHMENTS TABLE
    # ================================
    cur.execute("DROP TABLE IF EXISTS attachments;")
    cur.execute(
        """
        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            uploader_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (uploader_id) REFERENCES users(id)
        );
        """
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_attachments_post_id ON attachments(post_id);"
    )

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

    # Re-enable foreign keys for runtime
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # Create an initial user & post for testing if DEBUG mode is set to True
    if os.environ.get("DEBUG", "False").lower() in ("true", "1", "t"):
        print("DEBUG mode is enabled")
        create_initial_user(conn)
        print("Initial user created.")
        print("Email: user@domain.org")
        print("Password: Bonjour123!")
        print("MFA Secret: YOZSSE4QXLPRNCELINUIH6O2BXWLJVO4")
        create_initial_admin(conn)
        print("Initial admin created.")
        print("Email: admin@domain.org")
        print("Password: Bonjour123!")
        print("MFA Secret: ZBOAS52YBTNSZXHC35B6AJXCOOTZ4TTO")
        create_initial_post(conn)
        print("Initial post created.")
        print("Title: Welcome to the Blog!")
        print("Post is located at: /content/post/1")
        create_initial_private_post(conn)
        print("Initial private post created.")
        print("Title: Private Post")
        print("Post is located at: /content/post/2")
    conn.close()
    print(f"Database initialized successfully: {DB_FILE}")


def create_initial_user(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO users (
            id, email, password_hash, last_login, nb_failed_logins,
            created_at, activated, mfa_enabled, mfa_secret, backup_codes,
            role, disabled, disabled_by_admin
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            1,
            "user@domain.org",
            "scrypt:32768:8:1$0iGmdM53ifrZnXpX$78413db3ee07ba0fd89bcc2cd5ac9b8bcbe75c83eb8021a07be951887fd0848d5f0e711f484f2c8da25c8810fb9eaf7f24085b00a0bad3a6b10e451d1c01c2c6",
            "2025-12-08T20:10:12.482998",
            0,
            "2025-12-03T13:01:23.267399",
            1,
            1,
            "YOZSSE4QXLPRNCELINUIH6O2BXWLJVO4",
            '["e3aba907b83b", "ab237fb50db5", "3e1a0b59417c", "09cac10f2169", "ae8715439a60", "ec37c00a9217", "1cfdca3194bf", "a37cc97d5610"]',
            "user",
            0,
            0,
        ),
    )
    conn.commit()


def create_initial_admin(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO users (
            id, email, password_hash, last_login, nb_failed_logins,
            created_at, activated, mfa_enabled, mfa_secret, backup_codes,
            role, disabled, disabled_by_admin
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            2,
            "admin@domain.org",
            "scrypt:32768:8:1$0iGmdM53ifrZnXpX$78413db3ee07ba0fd89bcc2cd5ac9b8bcbe75c83eb8021a07be951887fd0848d5f0e711f484f2c8da25c8810fb9eaf7f24085b00a0bad3a6b10e451d1c01c2c6",
            "2025-12-08T20:10:12.482998",
            0,
            "2025-12-03T13:01:23.267399",
            1,
            1,
            "ZBOAS52YBTNSZXHC35B6AJXCOOTZ4TTO",
            '["823230f43476", "87ed321db154", "04d3848b5047", "39d32fb88843", "f057a4ade8d5", "a3a0b4a24f46", "0e139351f7ef", "92f460b242f7"]',
            "admin",
            0,
            0,
        ),
    )
    conn.commit()


def create_initial_post(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO posts (
            id, author_id, title, body, is_public, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            1,
            1,
            "Welcome to the Blog!",
            "This is the first post in the blog. Feel free to explore and create your own posts!",
            1,
            "2025-12-03T14:00:00.000000",
            "2025-12-03T14:00:00.000000",
        ),
    )
    conn.commit()


def create_initial_private_post(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO posts (
            id, author_id, title, body, is_public, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            2,
            1,
            "Private Post",
            "This is a private post. Only you can see this content.",
            0,
            "2025-12-03T15:00:00.000000",
            "2025-12-03T15:00:00.000000",
        ),
    )
    conn.commit()


if __name__ == "__main__":
    init_db()
