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


def get_user_posts(user_id, page=1, per_page=10):
    """Get paginated posts for a specific user (all posts - public and private)."""
    offset = (page - 1) * per_page
    posts = PostRepository.get_by_author(user_id, limit=per_page, offset=offset)
    return posts


def search_posts(query, limit=50):
    """Search posts."""
    if len(query) < 2:
        return []

    return PostRepository.search(query, limit=limit)


def get_by_post(post_id):
    """Get all comments for a post."""
    return CommentRepository.get_by_post(post_id)


def edit_post(post_id, user_id, title, body, is_public=True):
    """Edit a post (with permission check)."""
    if not permissions.can_edit_post(user_id, post_id):
        return PostResult(
            ok=False, errors=["You don't have permission to edit this post."]
        )

    errors = validators.validate_post_input(title, body, is_public)
    if errors:
        return PostResult(ok=False, errors=errors)

    PostRepository.update(post_id, title, body, is_public)
    return PostResult(ok=True, post_id=post_id)


def delete_post(post_id, user_id):
    """Delete a post (with permission check)."""
    if not permissions.can_delete_post(user_id, post_id):
        return PostResult(
            ok=False, errors=["You don't have permission to delete this post."]
        )

    PostRepository.delete(post_id)
    return PostResult(ok=True)


def add_comment(post_id, user_id, text):
    """Add a comment to a post."""
    errors = validators.validate_comment_input(text)
    if errors:
        return PostResult(ok=False, errors=errors)

    comment_id = CommentRepository.create(post_id, user_id, text)
    return PostResult(ok=True, post_id=comment_id)
