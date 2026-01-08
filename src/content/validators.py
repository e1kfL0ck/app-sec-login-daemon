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
