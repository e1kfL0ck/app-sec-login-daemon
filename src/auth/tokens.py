"""
Token handling utilities for auth workflows.
Manages generation, expiry, and validation of tokens.
"""

import secrets
from datetime import datetime, timedelta


def generate_activation_token():
    """Generate a secure random token for email activation."""
    return secrets.token_hex(32)


def generate_password_reset_token():
    """Generate a secure random token for password reset."""
    return secrets.token_hex(32)


def get_activation_token_expiry():
    """Return expiry datetime for activation tokens (24 hours from now)."""
    return datetime.now() + timedelta(hours=24)


def get_password_reset_token_expiry():
    """Return expiry datetime for password reset tokens (1 hour from now)."""
    return datetime.now() + timedelta(hours=1)


def is_token_expired(expires_at_str):
    """Check if a token (stored as ISO string) has expired."""
    try:
        expires_at = datetime.fromisoformat(expires_at_str)
        return datetime.now() > expires_at
    except (ValueError, TypeError):
        return True
