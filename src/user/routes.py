"""
User profile routes - profile page, account settings, email update, account deletion.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    session,
)
from session_helpers import login_required, admin_required

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


@user_bp.route("/profile/<int:target_user_id>")
@admin_required
def admin_view_profile(target_user_id):
    """Admin view for another user's profile."""
    user_data = services.get_user_profile(target_user_id)
    if not user_data:
        return render_template("404.html"), 404

    page = request.args.get("page", 1, type=int)
    posts = services.get_user_feed(target_user_id, page=page)

    return render_template(
        "profile.html",
        user=user_data,
        posts=posts,
        page=page,
        admin_view=True,
    )


@user_bp.route("/admin/users")
@admin_required
def admin_list_users():
    """Admin list of users with links to manage."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    users = services.get_all_users(page=page, per_page=per_page)
    return render_template(
        "admin_users.html", users=users, page=page, per_page=per_page
    )


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


@user_bp.route("/disable", methods=["POST"])
@login_required
def disable_account():
    """Self-service account disable. Content hidden from feeds."""
    user_id = session.get("user_id")
    password = request.form.get("password", "")
    confirmation = request.form.get("confirmation", "").strip()

    result = services.disable_user_account(user_id, password, confirmation)
    if result.ok:
        session.clear()
        return render_template(
            "index.html",
            success="Your account is now disabled. Contact an admin to re-enable if needed.",
        )

    user_data = services.get_user_profile(user_id)
    return render_template(
        "settings.html", user=user_data, disable_errors=result.errors
    )


@user_bp.route("/reactivate", methods=["POST"])
@login_required
def reactivate_account():
    """Reactivate a self-disabled account (not allowed if admin-disabled)."""
    user_id = session.get("user_id")
    password = request.form.get("password", "")

    result = services.reactivate_user_account(user_id, password)
    if result.ok:
        user_data = services.get_user_profile(user_id)
        session["disabled"] = False
        return render_template(
            "settings.html",
            user=user_data,
            success="Your account has been reactivated.",
        )

    user_data = services.get_user_profile(user_id)
    return render_template(
        "settings.html", user=user_data, reactivate_errors=result.errors
    )


@user_bp.route("/admin/<int:target_user_id>/disable", methods=["POST"])
@admin_required
def admin_disable_user(target_user_id):
    """Admin disables a user. User cannot self-reactivate."""
    # Prevent admin from disabling themselves to avoid lockout
    if session.get("user_id") == target_user_id:
        user_data = services.get_user_profile(target_user_id)
        return render_template(
            "profile.html",
            user=user_data,
            posts=services.get_user_feed(target_user_id),
            admin_view=True,
            admin_errors=["You cannot disable your own admin account."],
        )

    user_data = services.get_user_profile(target_user_id)
    if not user_data:
        return render_template("404.html"), 404

    result = services.admin_set_disabled(target_user_id, True)
    
    # Refetch user data to get updated status
    user_data = services.get_user_profile(target_user_id)
    
    return render_template(
        "profile.html",
        user=user_data,
        posts=services.get_user_feed(target_user_id),
        admin_view=True,
        admin_success="User account disabled." if result.ok else None,
        admin_errors=None if result.ok else result.errors,
    )


@user_bp.route("/admin/<int:target_user_id>/enable", methods=["POST"])
@admin_required
def admin_enable_user(target_user_id):
    """Admin re-enables a user account."""
    user_data = services.get_user_profile(target_user_id)
    if not user_data:
        return render_template("404.html"), 404

    result = services.admin_set_disabled(target_user_id, False)
    
    # Refetch user data to get updated status
    user_data = services.get_user_profile(target_user_id)
    
    return render_template(
        "profile.html",
        user=user_data,
        posts=services.get_user_feed(target_user_id),
        admin_view=True,
        admin_success="User account enabled." if result.ok else None,
        admin_errors=None if result.ok else result.errors,
    )


# TODO: Check this out
#
# @user_bp.route("/admin/<int:target_user_id>/activate", methods=["POST"])
# @admin_required
# def admin_activate_user(target_user_id):
#     """Admin activates a user (email activation flag)."""
#     user_data = services.get_user_profile(target_user_id)
#     if not user_data:
#         return render_template("404.html"), 404

#     result = services.admin_set_activation(target_user_id, True)
#     return render_template(
#         "profile.html",
#         user=user_data,
#         posts=services.get_user_feed(target_user_id),
#         admin_view=True,
#         admin_success="User activated." if result.ok else None,
#         admin_errors=None if result.ok else result.errors,
#     )

# TODO: Check this out
#
# @user_bp.route("/admin/<int:target_user_id>/deactivate", methods=["POST"])
# @admin_required
# def admin_deactivate_user(target_user_id):
#     """Admin deactivates a user (email activation flag)."""
#     user_data = services.get_user_profile(target_user_id)
#     if not user_data:
#         return render_template("404.html"), 404

#     result = services.admin_set_activation(target_user_id, False)
#     return render_template(
#         "profile.html",
#         user=user_data,
#         posts=services.get_user_feed(target_user_id),
#         admin_view=True,
#         admin_success="User deactivated." if result.ok else None,
#         admin_errors=None if result.ok else result.errors,
#     )
