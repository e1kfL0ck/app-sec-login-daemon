# Example: Building a Content Module Following the Same Pattern

This document shows how to build a new "content" module for the MicroBlog following the same encapsulation pattern as the auth module.

## Directory Structure

```bash
src/content/
├── __init__.py              # Blueprint definition
├── routes.py                # HTTP route handlers
├── services.py              # Business logic (create post, get posts, delete post, etc.)
├── repository.py            # Data access (PostRepository, CommentRepository)
├── validators.py            # Input validation
├── permissions.py           # Authorization checks (ownership, role-based)
├── templates/
│   ├── feed.html            # List all posts
│   ├── post_detail.html     # Single post view
│   ├── post_create.html     # Create post form
│   └── post_edit.html       # Edit post form
└── static/
    └── content.css
```

## Step-by-Step Implementation

### Step 1: Define the Blueprint

**`src/content/__init__.py`:**

```python
"""
Content module - encapsulates posts, comments, and content management.
Exposes a blueprint to be registered with the Flask app.
"""

from flask import Blueprint

# Create the content blueprint
content_bp = Blueprint("content", __name__, template_folder="templates")

# Import routes to register them with the blueprint
from . import routes  # noqa: F401

__all__ = ["content_bp"]
```

### Step 2: Validators

**`src/content/validators.py`:**

```python
"""
Validation utilities for content module.
"""

import field_utils as fu


def validate_post_input(title, body, is_public=True):
    """Validate post creation/edit inputs."""
    errors = []
    
    if not title or len(title.strip()) == 0:
        errors.append("Title is required.")
    elif len(title) > 255:
        errors.append("Title must be under 255 characters.")
    else:
        # Sanitize title
        errors += fu.sanitize_user_input(title, max_len=255)
    
    if not body or len(body.strip()) == 0:
        errors.append("Content is required.")
    elif len(body) > 10000:
        errors.append("Content must be under 10,000 characters.")
    else:
        # Sanitize body - allow newlines
        errors += fu.sanitize_user_input(body, max_len=10000)
    
    return errors


def validate_comment_input(text):
    """Validate comment input."""
    errors = []
    
    if not text or len(text.strip()) == 0:
        errors.append("Comment cannot be empty.")
    elif len(text) > 1000:
        errors.append("Comment must be under 1,000 characters.")
    else:
        errors += fu.sanitize_user_input(text, max_len=1000)
    
    return errors
```

### Step 3: Repository

**`src/content/repository.py`:**

```python
"""
Repository pattern for content data access.
"""

import sqlite3
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
            (author_id, title, body, is_public, created_at.isoformat(), created_at.isoformat()),
        )
        db.commit()
        post = db.execute(
            "SELECT id FROM posts WHERE author_id = ? ORDER BY created_at DESC LIMIT 1",
            (author_id,)
        ).fetchone()
        return post[0] if post else None
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID with author info."""
        db = get_db()
        return db.execute(
            """
            SELECT p.id, p.author_id, p.title, p.body, p.is_public, p.created_at, 
                   p.updated_at, u.email
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.id = ?
            """,
            (post_id,)
        ).fetchone()
    
    @staticmethod
    def get_public_posts(limit=50, offset=0):
        """Get all public posts (for feed)."""
        db = get_db()
        return db.execute(
            """
            SELECT p.id, p.author_id, p.title, p.body, p.created_at, u.email
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.is_public = 1
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
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
            SELECT p.id, p.author_id, p.title, p.body, p.created_at, u.email
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.is_public = 1 AND (p.title LIKE ? OR p.body LIKE ?)
            ORDER BY p.created_at DESC
            LIMIT ?
            """,
            (search_term, search_term, limit)
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
            (author_id, post_id)
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
            ORDER BY c.created_at ASC
            """,
            (post_id,)
        ).fetchall()
    
    @staticmethod
    def delete(comment_id):
        """Delete a comment."""
        db = get_db()
        db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        db.commit()
```

### Step 4: Permissions

**`src/content/permissions.py`:**

```python
"""
Authorization checks for content operations.
"""

from .repository import PostRepository


def can_view_post(user_id, post_id):
    """Check if user can view a post."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False
    
    # Public posts can be viewed by anyone
    if post[4]:  # is_public
        return True
    
    # Private posts can only be viewed by author
    if user_id == post[1]:  # author_id
        return True
    
    # TODO: Check if user is admin
    return False


def can_edit_post(user_id, post_id):
    """Check if user can edit a post."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False
    
    # Only author can edit
    return user_id == post[1]  # author_id


def can_delete_post(user_id, post_id):
    """Check if user can delete a post."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False
    
    # Author can delete own post
    if user_id == post[1]:
        return True
    
    # TODO: Check if user is admin
    return False
```

### Step 5: Services (Business Logic)

**`src/content/services.py`:**

```python
"""
Business logic for content operations.
"""

from . import validators, permissions
from .repository import PostRepository, CommentRepository


class PostResult:
    def __init__(self, ok, post_id=None, errors=None):
        self.ok = ok
        self.post_id = post_id
        self.errors = errors or []


def create_post(author_id, title, body, is_public=True):
    """Create a new post."""
    errors = validators.validate_post_input(title, body, is_public)
    if errors:
        return PostResult(ok=False, errors=errors)
    
    post_id = PostRepository.create(author_id, title, body, is_public)
    return PostResult(ok=True, post_id=post_id)


def get_post_view(post_id, requesting_user_id=None):
    """Get post for display (with permissions check)."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return None
    
    # Check permissions
    if not permissions.can_view_post(requesting_user_id, post_id):
        return None
    
    return post


def get_public_feed(page=1, per_page=10):
    """Get paginated public feed."""
    offset = (page - 1) * per_page
    posts = PostRepository.get_public_posts(limit=per_page, offset=offset)
    return posts


def search_posts(query, limit=50):
    """Search posts."""
    if len(query) < 2:
        return []
    
    return PostRepository.search(query, limit=limit)


def edit_post(post_id, user_id, title, body, is_public=True):
    """Edit a post (with permission check)."""
    if not permissions.can_edit_post(user_id, post_id):
        return PostResult(ok=False, errors=["You don't have permission to edit this post."])
    
    errors = validators.validate_post_input(title, body, is_public)
    if errors:
        return PostResult(ok=False, errors=errors)
    
    PostRepository.update(post_id, title, body, is_public)
    return PostResult(ok=True, post_id=post_id)


def delete_post(post_id, user_id):
    """Delete a post (with permission check)."""
    if not permissions.can_delete_post(user_id, post_id):
        return PostResult(ok=False, errors=["You don't have permission to delete this post."])
    
    PostRepository.delete(post_id)
    return PostResult(ok=True)
```

### Step 6: Routes

**`src/content/routes.py`:**

```python
"""
Content routes - posts, comments, search, feed.
"""

from flask import render_template, request, redirect, url_for, session
from session_helpers import login_required

from . import services, content_bp


@content_bp.route("/feed")
def feed():
    """Display public feed."""
    page = request.args.get('page', 1, type=int)
    posts = services.get_public_feed(page=page)
    
    return render_template("content/feed.html", posts=posts, page=page)


@content_bp.route("/post/<int:post_id>")
def view_post(post_id):
    """View a single post."""
    user_id = session.get("user_id")
    post = services.get_post_view(post_id, requesting_user_id=user_id)
    
    if not post:
        return render_template("404.html"), 404
    
    comments = CommentRepository.get_by_post(post_id)
    return render_template("content/post_detail.html", post=post, comments=comments)


@content_bp.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    """Create a new post."""
    user_id = session.get("user_id")
    
    if request.method == "GET":
        return render_template("content/post_create.html")
    
    # POST
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    is_public = request.form.get("is_public", "on") == "on"
    
    result = services.create_post(user_id, title, body, is_public)
    
    if not result.ok:
        return render_template("content/post_create.html", errors=result.errors)
    
    return redirect(url_for("content.view_post", post_id=result.post_id))


@content_bp.route("/search")
def search():
    """Search posts."""
    query = request.args.get("q", "").strip()
    
    if len(query) < 2:
        return render_template("content/search.html", posts=[], query=query)
    
    posts = services.search_posts(query)
    return render_template("content/search.html", posts=posts, query=query)
```

## Integration in Main App

**`src/app.py`:**

```python
from auth import auth_bp
from content import content_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)      # Routes at /register, /login, /logout, etc.
app.register_blueprint(content_bp)   # Routes at /feed, /post/<id>, /search, etc.
```

## Benefits

This approach ensures:

1. **Clear Separation** - Auth, content, admin, etc. are separate modules
2. **Reusability** - Each module can be reused in other apps
3. **Testability** - Services can be tested independently
4. **Security** - Permissions checked centrally in services
5. **Maintainability** - Each team member can work on one module

## Database Schema Extensions

```sql
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

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
```

---

By following this pattern, your MicroBlog grows in a controlled, maintainable way while keeping the authentication module cleanly separated.
