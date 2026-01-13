"""
Validators for user profile operations.
"""

import re


def validate_email_update(email):
    """
    Validate email for update operation.
    Returns list of error messages (empty if valid).
    """
    errors = []

    if not email:
        errors.append("Email is required")
        return errors

    # Basic email format validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        errors.append("Invalid email format")

    if len(email) > 254:
        errors.append("Email is too long")

    return errors


def validate_account_deletion(confirmation):
    """
    Validate account deletion confirmation.
    Returns list of error messages (empty if valid).
    """
    errors = []

    if not confirmation:
        errors.append("Confirmation is required")
        return errors

    # User must type "DELETE" to confirm
    if confirmation != "DELETE":
        errors.append("You must type DELETE to confirm account deletion")

    return errors
