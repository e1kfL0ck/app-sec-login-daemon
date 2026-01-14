"""
Repository pattern for content data access.
"""

from datetime import datetime
from db import get_db


class PostRepository:
    """Handles post-related database operations."""

    @staticmethod
    def create(author_id, title, body, is_public=True):
        """Create a new post. Returns post_id."""
        db = get_db()
        created_at = datetime.now()
        db.execute(
            """
            INSERT INTO posts (author_id, title, body, is_public, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                author_id,
                title,
                body,
                is_public,
                created_at.isoformat(),
                created_at.isoformat(),
            ),
        )
        db.commit()
        post = db.execute(
            "SELECT id FROM posts WHERE author_id = ? ORDER BY created_at DESC LIMIT 1",
            (author_id,),
        ).fetchone()
        return post[0] if post else None

    @staticmethod
    def get_by_id(post_id):
        """Get post by ID with author info."""
        db = get_db()
        return db.execute(
            """
             SELECT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at,
                 p.updated_at, u.email AS author_email, u.disabled AS author_disabled,
                 u.disabled_by_admin AS author_disabled_by_admin
             FROM posts p
             JOIN users u ON p.author_id = u.id
             WHERE p.id = ?
            """,
            (post_id,),
        ).fetchone()

    @staticmethod
    def get_public_posts(limit=50, offset=0):
        """Get all public posts (for feed)."""
        db = get_db()
        return db.execute(
            """
            SELECT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at,
                   u.email AS author_email
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.is_public = 1
              AND u.disabled = 0
              AND u.disabled_by_admin = 0
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    @staticmethod
    def get_all_posts(limit=50, offset=0):
        """Admin: get every post regardless of visibility or author status."""
        db = get_db()
        return db.execute(
            """
            SELECT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at,
                   u.email AS author_email, u.disabled AS author_disabled,
                   u.disabled_by_admin AS author_disabled_by_admin
            FROM posts p
            JOIN users u ON p.author_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    @staticmethod
    def get_by_author(author_id, limit=50, offset=0):
        """Get all posts by a specific author (including private posts).
        
        Allows self-disabled users to see their own posts, but filters out
        posts from admin-disabled users.
        """
        db = get_db()
        return db.execute(
            """
            SELECT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at,
                   u.email AS author_email
            FROM posts p
            JOIN users u ON p.author_id = u.id
                        WHERE p.author_id = ?
                            AND u.disabled_by_admin = 0
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (author_id, limit, offset),
        ).fetchall()

    @staticmethod
    def update(post_id, title, body, is_public=True):
        """Update an existing post."""
        db = get_db()
        db.execute(
            """
            UPDATE posts
            SET title = ?, body = ?, is_public = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, body, is_public, datetime.now().isoformat(), post_id),
        )
        db.commit()

    @staticmethod
    def delete(post_id):
        """Delete a post (hard delete or soft delete based on design)."""
        db = get_db()
        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()

    @staticmethod
    def search(query, limit=50):
        """Search posts by title or content."""
        db = get_db()
        search_term = f"%{query}%"
        return db.execute(
            """
            SELECT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at,
                   u.email AS author_email
            FROM posts p
            JOIN users u ON p.author_id = u.id
                        WHERE p.is_public = 1
                            AND u.disabled = 0
                            AND u.disabled_by_admin = 0
                            AND (p.title LIKE ? OR p.body LIKE ?)
            ORDER BY p.created_at DESC
            LIMIT ?
            """,
            (search_term, search_term, limit),
        ).fetchall()

    @staticmethod
    def search_by_attachment_filename(query, limit=50):
        """Search for posts that have attachments matching the query filename."""
        db = get_db()
        search_term = f"%{query}%"
        return db.execute(
            """
            SELECT DISTINCT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at,
                u.email AS author_email
            FROM posts p
            JOIN users u ON p.author_id = u.id
            JOIN attachments a ON p.id = a.post_id
                        WHERE p.is_public = 1
                            AND u.disabled = 0
                            AND u.disabled_by_admin = 0
                            AND (a.original_name LIKE ? OR a.stored_name LIKE ?)
            ORDER BY p.created_at DESC
            LIMIT ?
            """,
            (search_term, search_term, limit),
        ).fetchall()


class CommentRepository:
    """Handles comment-related database operations."""

    @staticmethod
    def create(author_id, post_id, text):
        """Create a new comment."""
        db = get_db()
        created_at = datetime.now()
        db.execute(
            """
            INSERT INTO comments (author_id, post_id, text, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (author_id, post_id, text, created_at.isoformat()),
        )
        db.commit()
        comment = db.execute(
            "SELECT id FROM comments WHERE author_id = ? AND post_id = ? ORDER BY created_at DESC LIMIT 1",
            (author_id, post_id),
        ).fetchone()
        return comment[0] if comment else None

    @staticmethod
    def get_by_post(post_id):
        """Get all comments for a post."""
        db = get_db()
        return db.execute(
            """
            SELECT c.id, c.author_id, c.text, c.created_at, u.email
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = ?
              AND u.disabled = 0
              AND u.disabled_by_admin = 0
            ORDER BY c.created_at ASC
            """,
            (post_id,),
        ).fetchall()

    @staticmethod
    def delete(comment_id):
        """Delete a comment."""
        db = get_db()
        db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        db.commit()


class AttachmentRepository:
    """Handles attachment-related database operations."""

    @staticmethod
    def create(post_id, uploader_id, original_name, stored_name, mime_type, size_bytes):
        """Create a new attachment and return its id."""
        db = get_db()
        created_at = datetime.now()
        db.execute(
            """
            INSERT INTO attachments (post_id, uploader_id, original_name, stored_name, mime_type, size_bytes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                uploader_id,
                original_name,
                stored_name,
                mime_type,
                size_bytes,
                created_at.isoformat(),
            ),
        )
        db.commit()
        row = db.execute(
            "SELECT id FROM attachments WHERE post_id = ? ORDER BY created_at DESC LIMIT 1",
            (post_id,),
        ).fetchone()
        return row[0] if row else None

    @staticmethod
    def get_by_post(post_id):
        """Get all attachments for a post."""
        db = get_db()
        return db.execute(
            """
            SELECT id, post_id, uploader_id, original_name, stored_name, mime_type, size_bytes, created_at
            FROM attachments
            WHERE post_id = ?
            ORDER BY created_at ASC
            """,
            (post_id,),
        ).fetchall()

    @staticmethod
    def get_by_id(attachment_id):
        """Get a single attachment by id."""
        db = get_db()
        return db.execute(
            """
            SELECT id, post_id, uploader_id, original_name, stored_name, mime_type, size_bytes, created_at
            FROM attachments
            WHERE id = ?
            """,
            (attachment_id,),
        ).fetchone()

    @staticmethod
    def delete(attachment_id):
        """Delete an attachment row."""
        db = get_db()
        db.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        db.commit()
