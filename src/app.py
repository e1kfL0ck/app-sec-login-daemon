import os
from datetime import datetime, timedelta
import secrets
import sqlite3
import uvicorn
import logging

from flask import Flask, request, render_template, url_for, session, redirect, abort
from werkzeug.security import generate_password_hash, check_password_hash
from asgiref.wsgi import WsgiToAsgi
from functools import wraps
from flask_wtf import CSRFProtect


from db import get_db, close_db

# Custom modules
import mail_handler
import field_utils

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

csrf = CSRFProtect(app)

logger = logging.getLogger(__name__)

# TODO: add if else for debug
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(name)s - %(message)s",
)


# Ensure database connection is closed after each request
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


# Ensure the user is logged in
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def already_logged_in(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


@app.errorhandler(404)
def not_found_error(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    app.logger.exception("Internal server error")
    app.logger.exception(e)
    return render_template("500.html"), 500


def validate_csrf():
    session_token = session.get("csrf_token")
    form_token = request.form.get("csrf_token")
    if not session_token or not form_token or session_token != form_token:
        abort(400)


@app.route("/")
@already_logged_in
def index():
    return render_template("index.html"), 200


@app.route("/register", methods=["GET", "POST"])
@already_logged_in
def register():
    if request.method == "GET":
        return render_template("register.html")

    # POST
    validate_csrf()
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = []
    errors += field_utils.sanitize_user_input(email)
    errors += field_utils.check_email_format(email)
    errors += field_utils.check_password_strength(password)
    errors += field_utils.check_password_match(password, confirm_password)

    if errors:
        return render_template("register.html", errors=errors)

    db = get_db()

    # User creation
    password_hash = generate_password_hash(password)
    created_at = datetime.now()

    try:
        db.execute(
            """
            INSERT INTO users (email, password_hash, created_at, activated)
            VALUES (?, ?, ?, ?)
            """,
            (email, password_hash, created_at.isoformat(), 0),
        )
        db.commit()

    except sqlite3.IntegrityError:
        errors.append("An account with this email already exists.")
        return render_template("register.html", errors=errors)

    user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]

    activation_token = secrets.token_hex(32)

    db.execute(
        """
        INSERT INTO tokens (token, user_id, expires_at, created_at, type)
        VALUES (?, ?, ?, ?, 'activation')
        """,
        (
            activation_token,
            user_id,
            (datetime.now() + timedelta(hours=24)).isoformat(),
            datetime.now().isoformat(),
        ),
    )
    db.commit()

    activation_link = url_for("activate", token=activation_token, _external=True)

    # Attempt to send activation email (logged on failure)
    mail_sent = False
    try:
        mail_sent = mail_handler.send_activation_email(email, activation_link)
    except Exception:
        # loggin is useless here, as mail_handler already logs exceptions
        # logger.exception("Unexpected error while sending activation email to %s", email)
        mail_sent = False

    if not mail_sent:
        # Show activation link on page if email sending fails or is skipped
        return render_template(
            "register.html",
            activation_link=activation_link,
            email=email,
            mail_sent=False,
        )

    # Successful registration message (email was sent)
    return render_template("register.html", email=email, mail_sent=True)


@app.route("/activate/<token>")
@already_logged_in
def activate(token):
    db = get_db()

    errors = field_utils.sanitize_user_input(token, max_len=64)

    if errors:
        return render_template(
            "activation_error.html", message="Invalid activation token."
        ), 400

    token_row = db.execute(
        "SELECT user_id, expires_at FROM tokens WHERE token = ? AND type = 'activation'",
        (token,),
    ).fetchone()

    if not token_row:
        return render_template(
            "activation_error.html", message="Invalid activation token."
        ), 400

    user_id, expires_at_str = token_row
    expires_at = datetime.fromisoformat(expires_at_str)

    if datetime.now() > expires_at:
        return render_template(
            "activation_error.html", message="Activation token has expired."
        ), 400

    db.execute("UPDATE users SET activated = 1 WHERE id = ?", (user_id,))
    db.commit()

    return render_template("activation_success.html")


@app.route("/forgotten_password", methods=["GET", "POST"])
def forgotten_password():
    """
    Following the click of the user on "I forgot my password":
    - queries user for an email
    - display confirmation message
    - if email is valid, sends a password reset token
    """
    # TODO: add check for the token in the GET method
    if request.method == "GET":
        return render_template("forgotten_password.html")

    # POST
    validate_csrf()
    email = request.form.get("email", "")

    errors = []
    errors += field_utils.sanitize_user_input(email)
    errors += field_utils.check_email_format(email)

    if errors:
        return render_template("forgotten_password.html", errors=errors)

    db = get_db()
    user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()

    if user is None:
        return render_template("forgotten_password.html", mail_sent=False)

    user_id = user[0]
    reset_token = secrets.token_hex(32)

    db.execute(
        """
        INSERT INTO tokens (token, user_id, expires_at, created_at, type)
        VALUES (?, ?, ?, ?, 'password_reset')
        """,
        (
            reset_token,
            user_id,
            (datetime.now() + timedelta(hours=1)).isoformat(),
            datetime.now().isoformat(),
        ),
    )
    db.commit()

    # TODO: build front for password reset
    reset_link = url_for("password_reset", token=reset_token, _external=True)
    # Attempt to send password reset email (logged on failure)
    mail_sent = False
    try:
        mail_sent = mail_handler.send_password_reset_email(email, reset_link)
    except Exception:
        # logging is useless here, as mail_handler already logs exceptions
        mail_sent = False

    if not mail_sent:
        # TODO: remove once dev is done
        # Show reset link on page if email sending fails or is skipped
        return render_template(
            "forgotten_password.html",
            reset_link=reset_link,
            email=email,
            mail_sent=False,
        )

    # Successful password reset message (email was sent)
    return render_template("forgotten_password.html", email=email, mail_sent=True)
    # message="If the email exists in our system, a password reset link has been sent."


@app.route("/password_reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    """
    Upon being requested by a token that the user received by mail, provides the password reset form :
    - checks password strength
    - checks that both password and password_confirmation match
    - replaces the account password in the database
    - displays a confirmation to the user
    """

    errors = field_utils.sanitize_user_input(token, max_len=64)

    db = get_db()

    if request.method == "GET":
        if errors:
            return render_template(
                "password_reset.html", message="Invalid activation token"
            ), 400

        token_row = db.execute(
            "SELECT user_id, expires_at FROM tokens WHERE token = ? AND type = 'password_reset'",
            (token,),
        ).fetchone()

        if not token_row:
            return render_template(
                "password_reset.html", message="Invalid activation token."
            ), 400

        user_id, expires_at_str = token_row
        expires_at = datetime.fromisoformat(expires_at_str)

        if datetime.now() > expires_at:
            return render_template(
                "password_reset.html", message="Activation token has expired."
            ), 400

        return render_template("password_reset.html")

        # TODO: expire token ?

    # POST
    validate_csrf()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = []
    errors += field_utils.check_password_strength(password)
    errors += field_utils.check_password_match(password, confirm_password)

    if errors:
        return render_template("password_reset.html", errors=errors)

    password_hash = generate_password_hash(password)
    # TODO: add field to track last password reset date?

    try:
        user_id = db.execute(
            "SELECT user_id FROM tokens WHERE token = ? AND type = 'password_reset'",
            (token,),
        ).fetchone()

        db.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (password_hash, user_id),
        )
        db.commit()

    except sqlite3.IntegrityError:
        logger.exception("Password database insertion failed.")
        message = "Password couldn't be updated due to an internal error."
        return render_template("register.html", message=message)

    db.commit()

    # Successful password reset message
    return render_template("password_reset.html", success=True)


@app.route("/login", methods=["GET", "POST"])
@already_logged_in
def login():
    if request.method == "GET":
        return render_template("login.html"), 200

    # POST
    validate_csrf()
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    if field_utils.sanitize_user_input(email):
        return render_template("login.html", errors=True)

    db = get_db()

    user_row = db.execute(
        "SELECT id, password_hash, nb_failed_logins, activated FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    if not user_row:
        return render_template("login.html", errors=True)

    user_id, db_password_hash, nb_failed_logins, activated = user_row

    # If password failed more than 3 times, you must change it
    if nb_failed_logins >= 3:
        return render_template("login.html", errors=False, reset=True)

    if not check_password_hash(db_password_hash, password) or not activated:
        db.execute(
            "UPDATE users SET nb_failed_logins = nb_failed_logins + 1 WHERE id = ? ",
            (user_id,),
        )
        db.commit()
        return render_template("login.html", errors=True)

    # Update last connexion time
    db.execute(
        "UPDATE users SET last_login = ? WHERE id = ?",
        (datetime.now().isoformat(), user_id),
    )
    db.commit()

    # Login successful
    session["user_id"] = user_id
    session["email"] = email

    # TODO: fix, we are still on /login
    return render_template("dashboard.html", user={"email": email}), 200


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user={"email": session.get("email")}), 200


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
