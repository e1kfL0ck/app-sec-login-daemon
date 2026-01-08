"""
Content module - encapsulates posts, comments, and content management.
Exposes a blueprint to be registered with the Flask app.
"""

from . import routes

# Export the blueprint
content_bp = routes.content_bp

__all__ = ["content_bp"]
