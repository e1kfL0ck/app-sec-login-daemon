"""
Validation utilities for auth module.
Wraps field_utils and provides cohesive validation for auth flows.
"""

import field_utils as fu


def validate_registration_input(email, password, confirm_password):
    """
    Validate registration form inputs.
    Returns list of error messages, or empty list if valid.
    """
    errors = []
    errors += fu.sanitize_user_input(email)
    errors += fu.check_email_format(email)
    errors += fu.check_password_strength(password)
    errors += fu.check_password_match(password, confirm_password)
    return errors


def validate_email_input(email):
    """Validate email format for password reset, etc."""
    errors = []
    errors += fu.sanitize_user_input(email)
    errors += fu.check_email_format(email)
    return errors


def validate_password_reset_input(password, confirm_password):
    """Validate password reset form inputs."""
    errors = []
    errors += fu.check_password_strength(password)
    errors += fu.check_password_match(password, confirm_password)
    return errors


def validate_login_input(email):
    """Validate login email input."""
    return fu.sanitize_user_input(email)


def validate_token_input(token, max_len=64):
    """Validate token format and length."""
    return fu.sanitize_user_input(token, max_len=max_len)
