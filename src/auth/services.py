"""
Business logic for auth workflows.
Orchestrates validation, repository calls, and email sending.
"""

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from . import validators, mail, tokens
from .repository import UserRepository, TokenRepository


class RegistrationResult:
    """Result object for registration operation."""

    def __init__(self, ok, errors=None, mail_sent=False):
        self.ok = ok
        self.errors = errors or []
        self.mail_sent = mail_sent


class LoginResult:
    """Result object for login operation."""

    def __init__(
        self,
        ok,
        user_id=None,
        error_msg=None,
        require_reset=False,
        mfa_enabled=False,
        role="user",
        disabled=False,
    ):
        self.ok = ok
        self.user_id = user_id
        self.error_msg = error_msg
        self.require_reset = require_reset
        self.mfa_enabled = mfa_enabled
        self.role = role
        self.disabled = disabled


def register_user(email, password, confirm_password):
    """
    Register a new user.
    Returns RegistrationResult with ok, errors, and mail_sent status.
    """
    # Validate inputs
    validation_errors = validators.validate_registration_input(
        email, password, confirm_password
    )
    if validation_errors:
        return RegistrationResult(ok=False, errors=validation_errors)

    # Try to create user
    password_hash = generate_password_hash(password)
    try:
        user_id = UserRepository.create(email, password_hash)
    except sqlite3.IntegrityError:
        return RegistrationResult(
            ok=False, errors=["An account with this email already exists."]
        )

    # Generate activation token
    activation_token = tokens.generate_activation_token()
    expiry = tokens.get_activation_token_expiry()
    TokenRepository.create(activation_token, user_id, expiry, "activation")

    # Send activation email
    mail_sent = mail.send_activation_email(email, activation_token)

    return RegistrationResult(ok=True, mail_sent=mail_sent)


def activate_user(token):
    """
    Activate a user account via token.
    Returns True if successful, False otherwise.
    """
    # Validate token format
    validation_errors = validators.validate_token_input(token, max_len=64)
    if validation_errors:
        return False

    # Get token from database
    token_row = TokenRepository.get_by_token(token, "activation")
    if not token_row:
        return False

    user_id, used, expires_at_str = token_row

    # Check if expired or already used
    if used or tokens.is_token_expired(expires_at_str):
        return False

    # Activate user and mark token as used
    UserRepository.activate(user_id)
    TokenRepository.mark_used(token)

    return True


def request_password_reset(email):
    """
    Request a password reset for an email address.
    Returns RegistrationResult (ok=False if email not found, ok=True regardless if email exists or not for security).
    """
    # Validate email format
    validation_errors = validators.validate_email_input(email)
    if validation_errors:
        # Return success to prevent email enumeration
        return RegistrationResult(ok=True, mail_sent=False)

    # Check if user exists
    user = UserRepository.get_by_email(email)
    if not user:
        # Return success to prevent email enumeration
        return RegistrationResult(ok=True, mail_sent=False)

    user_id = user[0]

    # Generate reset token
    reset_token = tokens.generate_password_reset_token()
    expiry = tokens.get_password_reset_token_expiry()
    TokenRepository.create(reset_token, user_id, expiry, "password_reset")

    # Send reset email
    mail_sent = mail.send_password_reset_email(email, reset_token)

    return RegistrationResult(ok=True, mail_sent=mail_sent)


def validate_password_reset_token(token):
    """
    Validate a password reset token.
    Returns user_id if valid, None otherwise.
    """
    # Validate token format
    validation_errors = validators.validate_token_input(token, max_len=64)
    if validation_errors:
        return None

    # Get token from database
    token_row = TokenRepository.get_by_token(token, "password_reset")
    if not token_row:
        return None

    user_id, used, expires_at_str = token_row

    # Check if expired or already used
    if used or tokens.is_token_expired(expires_at_str):
        return None

    return user_id


def reset_password(token, password, confirm_password):
    """
    Reset user password with token.
    Returns (ok, error_msg).
    """
    # Validate passwords
    validation_errors = validators.validate_password_reset_input(
        password, confirm_password
    )
    if validation_errors:
        return (False, validation_errors)

    # Validate token and get user_id
    user_id = validate_password_reset_token(token)
    if not user_id:
        return (False, ["Invalid or expired token."])

    # Update password
    try:
        password_hash = generate_password_hash(password)
        UserRepository.update_password(user_id, password_hash)
        TokenRepository.mark_used(token)
        return (True, None)
    except Exception as e:
        return (False, [f"Error resetting password: {str(e)}"])


def login_user(email, password):
    """
    Attempt to log in a user.
    Returns LoginResult with status and details.
    """
    # Validate email format
    if validators.validate_login_input(email):
        return LoginResult(ok=False, error_msg="Invalid email.")

    # Get user from database
    user = UserRepository.get_by_email(email)
    if not user:
        return LoginResult(ok=False, error_msg="Invalid email or password.")

    (
        user_id,
        password_hash,
        nb_failed_logins,
        activated,
        mfa_enabled,
        role,
        disabled,
        disabled_by_admin,
    ) = user

    # Check if account is locked after failed attempts
    if nb_failed_logins >= 3:
        return LoginResult(
            ok=False,
            require_reset=True,
            error_msg="Too many failed attempts. Password reset required.",
        )

    # Check password and activation
    if not check_password_hash(password_hash, password) or not activated:
        UserRepository.increment_failed_logins(user_id)
        return LoginResult(ok=False, error_msg="Invalid email or password.")

    # Account disabled by admin cannot log in
    if disabled_by_admin:
        return LoginResult(
            ok=False,
            error_msg="Your account has been disabled by an administrator.",
        )

    # Reset failed login counter on successful login
    UserRepository.reset_failed_logins(user_id)

    # Update last login time
    UserRepository.update_last_login(user_id)

    return LoginResult(
        ok=True,
        user_id=user_id,
        mfa_enabled=mfa_enabled,
        role=role,
        disabled=bool(disabled),
    )
