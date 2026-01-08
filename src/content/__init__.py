"""
Content module - encapsulates posts, comments, and content management.
Exposes a blueprint to be registered with the Flask app.
"""

from flask import Blueprint

# Create the content blueprint
content_bp = Blueprint("content", __name__, template_folder="templates")

# Import routes to register them with the blueprint
from . import routes  # noqa: F401

__all__ = ["content_bp"]
