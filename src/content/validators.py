"""
Validation utilities for content module.
"""

import field_utils as fu
import os
import magic
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


def detect_mime_from_content(file_stream):
    """Detect MIME type from actual file content using magic bytes.
    
    Args:
        file_stream: File stream object
        
    Returns:
        str: Detected MIME type or None if detection fails
    """
    try:
        # Save current position
        pos = file_stream.tell()
        # Read first 2048 bytes for magic detection
        file_stream.seek(0)
        header = file_stream.read(2048)
        # Restore position
        file_stream.seek(pos)
        
        if not header:
            return None
            
        # Detect MIME type from content
        mime = magic.from_buffer(header, mime=True)
        return mime.lower() if mime else None
    except (OSError, IOError, ValueError):
        # If detection fails due to I/O or value errors, return None
        return None


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


def validate_attachments(files):
    """Validate uploaded attachments list and return verified metadata.

    - Checks filename presence and safety
    - Enforces max file size
    - Validates MIME type from actual content (not client-provided)
    - Validates extension matches allowed types
    
    Returns:
        tuple: (errors list, validated_files list)
        where validated_files is a list of dicts with keys:
        - file_obj: the file object
        - original_name: sanitized filename
        - verified_mime: MIME type detected from content
    """
    errors = []
    validated = []
    
    if not files:
        return errors, validated

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
                f"Attachment '{original_name}': exceeds max size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )
            continue

        # Verify MIME type from actual file content
        detected_mime = detect_mime_from_content(f.stream)
        if not detected_mime:
            errors.append(f"Attachment '{original_name}': could not detect file type from content.")
            continue
            
        # Validate detected MIME type is in allowed list
        if detected_mime not in ALLOWED_MIME_TYPES:
            errors.append(
                f"Attachment '{original_name}': detected file type '{detected_mime}' is not allowed. "
                f"Only {', '.join(sorted(ALLOWED_MIME_TYPES))} are permitted."
            )
            continue

        # All validations passed - add to validated list
        validated.append({
            'file_obj': f,
            'original_name': safe_name,
            'verified_mime': detected_mime
        })

    return errors, validated
