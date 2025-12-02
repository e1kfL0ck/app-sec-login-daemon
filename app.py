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

DISALLOWED_CHARS = set("<>{};&")


# Ensure database connection is closed after each request
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


@app.route("/")
def index():
    return render_template(
        "base.html",
        title="Home – registration lab"
        ), 200,



def contains_dangerous_pattern(value: str) -> bool:
    """
    Check if the input contains dangerous patterns.
    Uses the global DANGEROUS_PATTERNS list.
    """
    if not value:
        return False
    for pat in DANGEROUS_PATTERNS:
        if pat.search(value):
            return True
    return False


def sanitize_user_input(field_value: str, max_len: int = 255) -> list[str]:
    """
    Check for safety and compliance of simple fields (email, pseudo, etc..) :
    - limit length
    - block some dangerous patterns
    - disallow certain characters
    """

    errors = []

    if field_value is None:
        errors.append("User input error.")
        return errors

    field_value = field_value.strip()  # Remove leading/trailing whitespace

    if len(field_value) > max_len:
        errors.append("User input error.")
        return errors

    if contains_dangerous_pattern(field_value):
        errors.append("User input error.")
        return errors

    if any(c in DISALLOWED_CHARS for c in field_value):
        errors.append("User input error.")
        return errors

    return errors


def check_email_format(email: str) -> list[str]:
    """
    Validate registration input fields and returns cleaned email and error list.
    """

    errors = []

    email = email.lower()

    if not email:
        errors.append("Email is required.")
    elif not EMAIL_REGEX.match(email):
        errors.append("Email format is invalid.")
    return errors


def check_password_strength(password: str) -> list[str]:
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")
    return errors


def check_password_match(password: str, confirm_password: str) -> list[str]:
    errors = []
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # POST
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = []
    errors += sanitize_user_input(email)
    errors += check_email_format(email)
    errors += check_password_strength(password)
    errors += check_password_match(password, confirm_password)

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
        errors.append("Email already registered.")
        return render_template("register.html", errors=errors)

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
        ),
    )
    db.commit()

    activation_link = url_for("activate", token=activation_token, _external=True)

    return render_template(
        "register.html", activation_link=activation_link, email=email
    )


@app.route("/activate/<token>")
def activate(token):
    db = get_db()

    token_row = db.execute(
        "SELECT user_id, expires_at FROM activation_tokens WHERE token = ?", (token,)
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

    return render_template(
        "activation_success.html",
    )


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
