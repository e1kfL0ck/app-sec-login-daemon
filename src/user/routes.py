"""
User profile routes - profile page, account settings, email update, account deletion.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    session,
)
from session_helpers import login_required

from . import services

user_bp = Blueprint("user", __name__, url_prefix="/user", template_folder="templates")


@user_bp.route("/profile")
@login_required
def profile():
    """Display user profile page with personal feed and account info."""
    user_id = session.get("user_id")
    user_data = services.get_user_profile(user_id)

    # Get user's recent posts
    page = request.args.get("page", 1, type=int)
    posts = services.get_user_feed(user_id, page=page)

    return render_template("profile.html", user=user_data, posts=posts, page=page)


@user_bp.route("/settings")
@login_required
def settings():
    """Display account settings page."""
    user_id = session.get("user_id")
    user_data = services.get_user_profile(user_id)

    return render_template("settings.html", user=user_data)


@user_bp.route("/update-email", methods=["POST"])
@login_required
def update_email():
    """Update user email address."""
    user_id = session.get("user_id")
    new_email = request.form.get("new_email", "").strip()
    password = request.form.get("password", "")

    result = services.update_user_email(user_id, new_email, password)

    if result.ok:
        # Update session email
        session["email"] = new_email
        return render_template(
            "settings.html",
            user={"email": new_email},
            success="Email updated successfully!",
        )
    else:
        user_data = services.get_user_profile(user_id)
        return render_template("settings.html", user=user_data, errors=result.errors)


@user_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    """Delete user account."""
    user_id = session.get("user_id")
    password = request.form.get("password", "")
    confirmation = request.form.get("confirmation", "").strip()

    result = services.delete_user_account(user_id, password, confirmation)

    if result.ok:
        # Clear session and redirect to home
        session.clear()
        return render_template(
            "index.html", success="Your account has been successfully deleted."
        )
    else:
        user_data = services.get_user_profile(user_id)
        return render_template(
            "settings.html", user=user_data, delete_errors=result.errors
        )
