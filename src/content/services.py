"""
Business logic for content operations.
"""

from . import validators, permissions
import os
import uuid
import magic
from .repository import PostRepository, CommentRepository, AttachmentRepository


class PostResult:
    def __init__(self, ok, post_id=None, errors=None):
        self.ok = ok
        self.post_id = post_id
        self.errors = errors or []


UPLOAD_ROOT = "/data/uploads"


def _ensure_post_upload_dir(post_id):
    d = os.path.join(UPLOAD_ROOT, str(post_id))
    os.makedirs(d, exist_ok=True)
    return d


def _save_attachments(post_id, uploader_id, validated_files):
    """Save validated attachments to disk and database.
    
    Args:
        post_id: The post ID to attach files to
        uploader_id: The user ID uploading the files
        validated_files: List of dicts from validate_attachments with keys:
            - file_obj: the file object
            - original_name: sanitized filename
            - verified_mime: MIME type detected from content
    
    Returns:
        List of attachment IDs created
    """
    if not validated_files:
        return []

    saved_ids = []
    target_dir = _ensure_post_upload_dir(post_id)

    for file_meta in validated_files:
        f = file_meta['file_obj']
        original_name = file_meta['original_name']
        verified_mime = file_meta['verified_mime']

        _, ext = os.path.splitext(original_name)
        stored_name = f"{uuid.uuid4().hex}{ext.lower()}"
        stored_path = os.path.join(target_dir, stored_name)

        # Persist file to disk
        f.stream.seek(0)
        with open(stored_path, "wb") as out:
            out.write(f.read())

        # Get size again from the saved file to be accurate
        size_bytes = os.path.getsize(stored_path)
        attachment_id = AttachmentRepository.create(
            post_id,
            uploader_id,
            original_name,
            stored_name,
            verified_mime,  # Use verified MIME type, not client-provided
            size_bytes,
        )
        if attachment_id:
            saved_ids.append(attachment_id)

    return saved_ids


def create_post(author_id, title, body, is_public=True, files=None):
    """Create a new post."""
    errors = validators.validate_post_input(title, body)
    # Validate attachments and get verified metadata
    attachment_errors, validated_files = validators.validate_attachments(files or [])
    errors += attachment_errors
    if errors:
        return PostResult(ok=False, errors=errors)

    post_id = PostRepository.create(author_id, title, body, is_public)
    # Save attachments if any
    _save_attachments(post_id, author_id, validated_files)
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


def edit_post(post_id, user_id, title, body, is_public=True, files=None):
    """Edit a post (with permission check)."""
    if not permissions.can_edit_post(user_id, post_id):
        return PostResult(
            ok=False, errors=["You don't have permission to edit this post."]
        )

    errors = validators.validate_post_input(title, body)
    attachment_errors, validated_files = validators.validate_attachments(files or [])
    errors += attachment_errors
    if errors:
        return PostResult(ok=False, errors=errors)

    PostRepository.update(post_id, title, body, is_public)
    _save_attachments(post_id, user_id, validated_files)
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


def get_attachments_for_post(post_id):
    return AttachmentRepository.get_by_post(post_id)


def get_attachment_file(attachment_id, requesting_user_id=None):
    """Return tuple (directory, stored_name, original_name, mime_type) if user can view it, else None.
    
    Re-validates MIME type from file content for defense-in-depth.
    """
    att = AttachmentRepository.get_by_id(attachment_id)
    if not att:
        return None

    post_id = att["post_id"]
    if not permissions.can_view_post(requesting_user_id, post_id):
        return None

    directory = _ensure_post_upload_dir(post_id)
    stored_name = att["stored_name"]
    original_name = att["original_name"]
    stored_mime = att["mime_type"]
    
    # Re-verify MIME type from actual file content for defense-in-depth
    file_path = os.path.join(directory, stored_name)
    if os.path.exists(file_path):
        try:
            # Read file and verify MIME type using magic bytes
            with open(file_path, 'rb') as f:
                header = f.read(2048)
                if header:
                    detected_mime = magic.from_buffer(header, mime=True)
                    # Use detected MIME type if available, otherwise fall back to stored
                    mime_type = detected_mime.lower() if detected_mime else stored_mime
                else:
                    mime_type = stored_mime
        except Exception:
            # If verification fails, use stored MIME type
            mime_type = stored_mime
    else:
        mime_type = stored_mime
    
    return directory, stored_name, original_name, mime_type
