"""
Repository pattern for auth data access.
Encapsulates all database queries related to users and tokens.
"""

from datetime import datetime
from db import get_db


class UserRepository:
    """Handles user-related database operations."""

    @staticmethod
    def create(email, password_hash):
        """
        Create a new user.
        Raises sqlite3.IntegrityError if email already exists.
        Returns user_id.
        """
        db = get_db()
        created_at = datetime.now()
        db.execute(
            """
            INSERT INTO users (email, password_hash, created_at, activated)
            VALUES (?, ?, ?, ?)
            """,
            (email, password_hash, created_at.isoformat(), 0),
        )
        db.commit()
        user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        return user[0] if user else None

    @staticmethod
    def get_by_email(email):
        """Get user by email. Returns row with credentials and flags."""
        db = get_db()
        return db.execute(
            """
            SELECT id, password_hash, nb_failed_logins, activated,
                   mfa_enabled, role, disabled, disabled_by_admin
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID. Returns user row or None."""
        db = get_db()
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    @staticmethod
    def activate(user_id):
        """Mark user as activated."""
        db = get_db()
        db.execute("UPDATE users SET activated = 1 WHERE id = ?", (user_id,))
        db.commit()

    @staticmethod
    def increment_failed_logins(user_id):
        """Increment failed login counter."""
        db = get_db()
        db.execute(
            "UPDATE users SET nb_failed_logins = nb_failed_logins + 1 WHERE id = ?",
            (user_id,),
        )
        db.commit()

    @staticmethod
    def reset_failed_logins(user_id):
        """Reset failed login counter."""
        db = get_db()
        db.execute("UPDATE users SET nb_failed_logins = 0 WHERE id = ?", (user_id,))
        db.commit()

    @staticmethod
    def update_last_login(user_id):
        """Update last login timestamp."""
        db = get_db()
        db.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id),
        )
        db.commit()

    @staticmethod
    def update_password(user_id, password_hash):
        """Update user password."""
        db = get_db()
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )
        db.commit()


class TokenRepository:
    """Handles token-related database operations."""

    @staticmethod
    def create(token, user_id, expires_at, token_type):
        """Create a new token."""
        db = get_db()
        db.execute(
            """
            INSERT INTO tokens (token, user_id, expires_at, created_at, type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                token,
                user_id,
                expires_at.isoformat(),
                datetime.now().isoformat(),
                token_type,
            ),
        )
        db.commit()

    @staticmethod
    def get_by_token(token, token_type):
        """
        Get token by token string and type.
        Returns (user_id, used, expires_at) or None.
        """
        db = get_db()
        return db.execute(
            "SELECT user_id, used, expires_at FROM tokens WHERE token = ? AND type = ?",
            (token, token_type),
        ).fetchone()

    @staticmethod
    def mark_used(token):
        """Mark token as used."""
        db = get_db()
        db.execute("UPDATE tokens SET used = 1 WHERE token = ?", (token,))
        db.commit()

    @staticmethod
    def invalidate_all_of_type_for_user(user_id, token_type):
        """Mark all tokens of a given type for a user as used."""
        db = get_db()
        db.execute(
            "UPDATE tokens SET used = 1 WHERE user_id = ? AND type = ?",
            (user_id, token_type),
        )
        db.commit()
