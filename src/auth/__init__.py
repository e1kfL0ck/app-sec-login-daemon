"""
Auth module - encapsulates registration, login, password reset, and MFA workflows.
Exposes a blueprint to be registered with the Flask app.
"""

# Import routes first to define auth_bp
from . import routes

# Export the blueprint
auth_bp = routes.auth_bp

__all__ = ["auth_bp"]
