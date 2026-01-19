"""
Business logic for user profile and account management.
"""

import sqlite3
from werkzeug.security import check_password_hash

from .validators import (
    validate_email_update,
    validate_account_deletion,
    validate_account_disable,
)
from .repository import UserProfileRepository


class UpdateEmailResult:
    """Result object for email update operation."""

    def __init__(self, ok, errors=None):
        self.ok = ok
        self.errors = errors or []


class DeleteAccountResult:
    """Result object for account deletion operation."""

    def __init__(self, ok, errors=None):
        self.ok = ok
        self.errors = errors or []


def get_user_profile(user_id):
    """
    Get user profile data.
    Returns user dict with email and other info.
    """
    user = UserProfileRepository.get_user_by_id(user_id)
    if not user:
        return None

    return {
        "id": user[0],
        "email": user[1],
        "created_at": user[3],
        "activated": user[4],
        "mfa_enabled": user[5],
        "role": user[6],
        "disabled": bool(user[7]),
        "disabled_by_admin": bool(user[8]),
    }


def get_user_feed(user_id, page=1, per_page=10):
    """
    Get user's personal feed (their own posts).
    Returns list of posts.
    """
    # Import here to avoid circular dependency
    from content import services as content_services

    return content_services.get_user_posts(user_id, page=page, per_page=per_page)


def get_all_users(page=1, per_page=50):
    """Admin: list users with basic info."""
    offset = (page - 1) * per_page
    return UserProfileRepository.list_users(limit=per_page, offset=offset)


def update_user_email(user_id, new_email, password):
    """
    Update user's email address.
    Requires password confirmation.
    Returns UpdateEmailResult.
    """
    # Validate inputs
    validation_errors = validate_email_update(new_email)
    if validation_errors:
        return UpdateEmailResult(ok=False, errors=validation_errors)

    # Get current user
    user = UserProfileRepository.get_user_by_id(user_id)
    if not user:
        return UpdateEmailResult(ok=False, errors=["User not found"])

    # Verify password
    password_hash = user[2]  # password_hash is at index 2
    if not check_password_hash(password_hash, password):
        return UpdateEmailResult(ok=False, errors=["Incorrect password"])

    # Check if new email is same as current
    current_email = user[1]
    if current_email == new_email:
        return UpdateEmailResult(
            ok=False, errors=["New email is the same as current email"]
        )

    # Check if new email already exists
    existing_user = UserProfileRepository.get_user_by_email(new_email)
    if existing_user:
        return UpdateEmailResult(ok=False, errors=["Email already in use"])

    # Update email
    try:
        UserProfileRepository.update_email(user_id, new_email)
        return UpdateEmailResult(ok=True)
    except sqlite3.IntegrityError:
        return UpdateEmailResult(ok=False, errors=["Email already in use"])
    except Exception as e:
        return UpdateEmailResult(ok=False, errors=[f"Failed to update email: {str(e)}"])


def delete_user_account(user_id, password, confirmation):
    """
    Delete user account permanently.
    Requires password and typed confirmation.
    Returns DeleteAccountResult.
    """
    # Validate inputs
    validation_errors = validate_account_deletion(confirmation)
    if validation_errors:
        return DeleteAccountResult(ok=False, errors=validation_errors)

    # Get current user
    user = UserProfileRepository.get_user_by_id(user_id)
    if not user:
        return DeleteAccountResult(ok=False, errors=["User not found"])

    # Verify password
    password_hash = user[2]
    if not check_password_hash(password_hash, password):
        return DeleteAccountResult(ok=False, errors=["Incorrect password"])

    # Delete user account
    try:
        UserProfileRepository.delete_user(user_id)
        return DeleteAccountResult(ok=True)
    except Exception as e:
        return DeleteAccountResult(
            ok=False, errors=[f"Failed to delete account: {str(e)}"]
        )


class ToggleAccountResult:
    """Result for disable/reactivate operations."""

    def __init__(self, ok, errors=None):
        self.ok = ok
        self.errors = errors or []


def disable_user_account(user_id, password, confirmation):
    """
    Disable a user account (self-service). Content becomes hidden.
    Requires password and typed confirmation.
    """
    validation_errors = validate_account_disable(confirmation)
    if validation_errors:
        return ToggleAccountResult(ok=False, errors=validation_errors)

    user = UserProfileRepository.get_user_by_id(user_id)
    if not user:
        return ToggleAccountResult(ok=False, errors=["User not found"])

    if bool(user["disabled_by_admin"]):
        return ToggleAccountResult(
            ok=False,
            errors=["Account disabled by administrator. Contact support."],
        )

    if not check_password_hash(user["password_hash"], password):
        return ToggleAccountResult(ok=False, errors=["Incorrect password"])

    try:
        UserProfileRepository.set_disabled(user_id, True, False)
        return ToggleAccountResult(ok=True)
    except Exception as e:
        return ToggleAccountResult(
            ok=False, errors=[f"Failed to disable account: {str(e)}"]
        )


def reactivate_user_account(user_id, password):
    """
    Reactivate a self-disabled account. Not allowed if disabled by admin.
    """
    user = UserProfileRepository.get_user_by_id(user_id)
    if not user:
        return ToggleAccountResult(ok=False, errors=["User not found"])

    if bool(user["disabled_by_admin"]):
        return ToggleAccountResult(
            ok=False,
            errors=["Account disabled by administrator. Contact support."],
        )

    if not bool(user["disabled"]):
        return ToggleAccountResult(ok=False, errors=["Account is already active"])

    if not check_password_hash(user["password_hash"], password):
        return ToggleAccountResult(ok=False, errors=["Incorrect password"])

    try:
        UserProfileRepository.set_disabled(user_id, False, False)
        return ToggleAccountResult(ok=True)
    except Exception as e:
        return ToggleAccountResult(
            ok=False, errors=[f"Failed to reactivate account: {str(e)}"]
        )


def admin_set_disabled(target_user_id, disabled=True):
    """Admin disable/enable a user account."""
    try:
        UserProfileRepository.set_disabled(target_user_id, disabled, disabled)
        return ToggleAccountResult(ok=True)
    except Exception as e:
        return ToggleAccountResult(
            ok=False, errors=[f"Failed to update status: {str(e)}"]
        )
