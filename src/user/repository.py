"""
Repository pattern for user profile data access.
"""

from db import get_db


class UserProfileRepository:
    """Handles user profile-related database operations."""

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID. Returns user row or None."""
        db = get_db()
        return db.execute(
            """
            SELECT id, email, password_hash, created_at, activated,
                   mfa_enabled, role, disabled, disabled_by_admin, last_login
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    @staticmethod
    def get_user_by_email(email):
        """Get user by email. Returns user row or None."""
        db = get_db()
        return db.execute(
            "SELECT id, email, password_hash, role, disabled, disabled_by_admin FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    @staticmethod
    def update_email(user_id, new_email):
        """Update user email address."""
        db = get_db()
        db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
        db.commit()

    @staticmethod
    def set_disabled(user_id, disabled, disabled_by_admin=False):
        """Enable or disable a user account."""
        db = get_db()
        db.execute(
            """
            UPDATE users
            SET disabled = ?, disabled_by_admin = ?
            WHERE id = ?
            """,
            (1 if disabled else 0, 1 if disabled_by_admin else 0, user_id),
        )
        db.commit()

    @staticmethod
    def delete_user(user_id):
        """
        Delete user account and all associated data.
        This includes posts, comments, and tokens.
        """
        db = get_db()

        # Delete user's comments first (foreign key constraint)
        db.execute("DELETE FROM comments WHERE author_id = ?", (user_id,))

        # Delete user's posts
        db.execute("DELETE FROM posts WHERE author_id = ?", (user_id,))

        # Delete user's tokens
        db.execute("DELETE FROM tokens WHERE user_id = ?", (user_id,))

        # Finally, delete the user
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))

        db.commit()

    @staticmethod
    def list_users(limit=50, offset=0):
        """Return basic info for users for admin listing."""
        db = get_db()
        return db.execute(
            """
            SELECT id, email, role, activated, disabled, disabled_by_admin, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
