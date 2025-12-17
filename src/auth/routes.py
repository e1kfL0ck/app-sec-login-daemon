"""
Auth routes - registration, login, password reset, activation, and logout.
Uses services layer for business logic.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for
from session_helpers import login_required, already_logged_in

from . import services

# Create the blueprint here to avoid circular imports
auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/register", methods=["GET", "POST"])
@already_logged_in
def register():
    if request.method == "GET":
        return render_template("register.html")

    # POST
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    result = services.register_user(email, password, confirm_password)

    if not result.ok:
        return render_template("register.html", errors=result.errors)

    return render_template("register.html", email=email, mail_sent=result.mail_sent)


@auth_bp.route("/activate/<token>")
@already_logged_in
def activate(token):
    ok = services.activate_user(token)
    return render_template("activation.html", success=ok), (200 if ok else 400)


@auth_bp.route("/forgotten_password", methods=["GET", "POST"])
def forgotten_password():
    """
    Handle forgotten password requests.
    GET: Display form.
    POST: Process email and send reset token.
    """
    if request.method == "GET":
        return render_template("forgotten_password.html")

    # POST
    email = request.form.get("email", "")
    result = services.request_password_reset(email)

    # Always show success for security (prevent email enumeration)
    return render_template(
        "forgotten_password.html", email=email, mail_sent=result.mail_sent
    )


@auth_bp.route("/password_reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    """
    Handle password reset via token.
    GET: Validate token and display form.
    POST: Reset password.
    """
    if request.method == "GET":
        user_id = services.validate_password_reset_token(token)
        if not user_id:
            return render_template(
                "password_reset.html", success=False, token=token
            ), 400
        return render_template("password_reset.html", token=token)

    # POST
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    ok, errors = services.reset_password(token, password, confirm_password)

    if not ok:
        return render_template("password_reset.html", errors=errors, token=token), 400

    return render_template("password_reset.html", success=True, token=token)


@auth_bp.route("/login", methods=["GET", "POST"])
@already_logged_in
def login():
    if request.method == "GET":
        return render_template("login.html"), 200

    # POST
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    result = services.login_user(email, password)

    if not result.ok:
        if result.require_reset:
            return render_template("login.html", errors=False, reset=True)
        return render_template("login.html", errors=True)

    # Login successful
    session.clear()  # mitigate session fixation

    if result.mfa_enabled:
        session["pre_auth_user_id"] = result.user_id
        return redirect(url_for("mfa.verify"))

    session["user_id"] = result.user_id
    session["email"] = email
    return redirect(url_for("dashboard"))


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))
