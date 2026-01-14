"""
Validators for user profile operations.
"""

import field_utils as fu


def validate_email_update(email):
    """
    Validate email for update operation.
    Returns a list of errors (empty if valid).
    """
    errors = []

    errors += fu.sanitize_user_input_obfuscated(email)
    errors += fu.check_email_format(email)

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


def validate_account_disable(confirmation):
    """
    Validate account disable confirmation.
    Users must type DISABLE to proceed.
    """
    errors = []
    if not confirmation:
        errors.append("Confirmation is required")
        return errors

    if confirmation != "DISABLE":
        errors.append("You must type DISABLE to confirm account disablement")

    return errors
