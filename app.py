import os
import re
from datetime import datetime, timedelta
import secrets
import sqlite3
import uvicorn
import logging

from flask import Flask, request, render_template, url_for
from werkzeug.security import generate_password_hash
from asgiref.wsgi import WsgiToAsgi

from db import get_db, close_db

app = Flask(__name__)

logger = logging.getLogger(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

DANGEROUS_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # onclick=, onerror=, etc.
    re.compile(r"javascript\s*:", re.IGNORECASE),
]

DISALLOWED_CHARS_SIMPLE = set("<>{};&")


@app.teardown_appcontext
def teardown_db(exception):
    close_db()


@app.route("/")
def index():
    return "Home – registration lab"


def contains_dangerous_pattern(value: str) -> bool:
    if not value:
        return False
    for pat in DANGEROUS_PATTERNS:
        if pat.search(value):
            return True
    return False


def validate_safe_simple_field(
    field_value: str, errors: list[str], max_len: int = 255
):
    """
    Check for safety and compliance of simple fields (email, pseudo, etc..) :
    - disallow certain characters
    - limit length
    - block some dangerous patterns
    """

    if field_value is None:
        errors.append("User input error.")
        return ""

    field_value = field_value.strip()

    if len(field_value) > max_len:
        errors.append("User input error: field is too long")
        return ""

    if contains_dangerous_pattern(field_value):
        errors.append("User input error.")
        return ""

    if any(c in DISALLOWED_CHARS_SIMPLE for c in field_value):
        errors.append("User input error.")
        return ""

    return field_value


def sanitize_user_input(email: str, password: str, confirm_password: str):
    """
    Validate registration input fields and returns cleaned email and error list.
    """

    errors = []

    email = validate_safe_simple_field(email, "Email", errors, max_len=255)
    email = email.lower()

    if not email:
        errors.append("Email is required.")
    elif not EMAIL_REGEX.match(email):
        errors.append("Email format is invalid.")

    # TODO : add password sanitation and strength checks

    password = password or ""
    confirm_password = confirm_password or ""

    if not password or not confirm_password:
        errors.append("Password and confirmation are required.")
    else:
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            errors.append("Password must contain at least one letter and one digit.")

    return errors


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # POST
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = sanitize_user_input(email, password, confirm_password)

    if errors:
        return render_template("register.html", errors=errors, email=email)

    db = get_db()

    # Création de l'utilisateur
    password_hash = generate_password_hash(password)
    created_at = datetime.now()

    try:
        db.execute(
            """
            INSERT INTO users (email, password_hash, created_at, activated)
            VALUES (?, ?, ?, ?)
            """,
            (email, password_hash, created_at.isoformat(), 0)
        )
        db.commit()

    except sqlite3.IntegrityError:
        errors.append("Email already registered.")
        return render_template("register.html", errors=errors, email=email)

    user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]

    activation_token = secrets.token_hex(32)

    db.execute(
        """
        INSERT INTO activation_tokens (token, user_id, expires_at, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            activation_token,
            user_id,
            (datetime.now() + timedelta(hours=24)).isoformat(),
            datetime.now().isoformat(),
        )
    )
    db.commit()

    #TODO: sqlite3.IntegrityError: UNIQUE constraint failed: users.email pas renvoyée

    activation_link = url_for("activate", token=activation_token, _external=True)

    db.close()

    return render_template(
        "register.html",
        activation_link=activation_link,
        email=email,
    )

@app.route("/activate/<token>")
def activate(token):
    db = get_db()

    token_row = db.execute(
        "SELECT user_id, expires_at FROM activation_tokens WHERE token = ?", (token,)
    ).fetchone()

    if not token_row:
        return "Invalid or expired activation token.", 400

    user_id, expires_at_str = token_row
    expires_at = datetime.fromisoformat(expires_at_str)

    if datetime.now() > expires_at:
        return "Activation token has expired.", 400

    db.execute(
        "UPDATE users SET activated = 1 WHERE id = ?", (user_id,)
    )
    db.commit()

    return "Account successfully activated. You can now log in."


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
