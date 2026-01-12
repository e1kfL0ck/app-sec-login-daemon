"""
Validation utilities for content module.
"""

import field_utils as fu
import os
import mimetypes
from werkzeug.utils import secure_filename

# Basic file validation settings
ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
}

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".txt",
}

# 5 MB limit per file
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


def validate_post_input(title, body):
    """Validate post creation/edit inputs."""
    errors = []
    errors += fu.sanitize_user_input_explicit(title, max_len=255, field_name="Title")
    errors += fu.sanitize_user_input_explicit(body, max_len=10000, field_name="Content")
    return errors


def validate_comment_input(text):
    """Validate comment input."""
    errors = []
    errors += fu.sanitize_user_input_explicit(text, max_len=1000, field_name="Comment")
    return errors


def validate_search_query(text):
    """Validate search query input."""
    errors = []
    errors += fu.sanitize_user_input_explicit(
        text, max_len=200, field_name="Search Query"
    )
    # Avoid database overload with very short queries
    if len(text.strip()) < 2:
        errors.append("Search query must be at least 2 characters long.")
    return errors


def validate_attachments(files):
    """Validate uploaded attachments list.

    - Checks filename presence and safety
    - Enforces max file size
    - Validates MIME type and extension
    """
    errors = []
    if not files:
        return errors

    for f in files:
        if not f:
            errors.append("Invalid attachment provided.")
            continue

        # Filename safety
        original_name = (f.filename or "").strip()
        if not original_name:
            errors.append("Attachment must have a filename.")
            continue

        safe_name = secure_filename(original_name)
        if not safe_name:
            errors.append("Attachment filename is invalid.")
            continue

        # Extension check
        _, ext = os.path.splitext(safe_name)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"Attachment '{original_name}': file type not allowed.")
            continue

        # Size check (seek to end, then restore position)
        try:
            pos = f.stream.tell()
            f.stream.seek(0, os.SEEK_END)
            size = f.stream.tell()
            f.stream.seek(pos)
        except Exception:
            size = None

        if size is None or size <= 0:
            errors.append(f"Attachment '{original_name}': could not determine size.")
            continue

        if size > MAX_FILE_SIZE_BYTES:
            errors.append(
                f"Attachment '{original_name}': exceeds max size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )
            continue

        # MIME type check: combine client-provided and guessed types
        client_mime = (f.mimetype or "").lower()
        guessed_mime, _ = mimetypes.guess_type(safe_name)
        guessed_mime = (guessed_mime or "").lower()

        effective_mime = client_mime or guessed_mime
        if not effective_mime:
            errors.append(f"Attachment '{original_name}': unknown MIME type.")
            continue

        if effective_mime not in ALLOWED_MIME_TYPES:
            errors.append(f"Attachment '{original_name}': MIME type not allowed.")
            continue

    return errors
