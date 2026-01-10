"""
Validation utilities for content module.
"""

import field_utils as fu


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
