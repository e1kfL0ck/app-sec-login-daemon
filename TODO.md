# TODO

This file lists high-level tasks and function contracts for the login/registration/activation daemon. Each section contains the expected inputs, behavior, and returned template/result.

## Urgent

- Implement a mitigation to prevent password-reset mail requests spam
- Implement a mitigation to prevent bruteforce on 2FA? (or test if by default it works)

## Optional features TODO

- CSRF ok, to be added directly into headers.
- Rate limiting / Captcha (simple maths ? / retype something ?)
- security events logging
- HTTPS
- mail sending delay is different if the mail is sent or not

## Nginx (deployment)

- Rate limiting (IP / endpoint).
- Redirection HTTP -> HTTPS. Enforced.
- Make sure static resources are exposed.

## Optional features TODO from past iterations

- Password strength meter
- Email domain whitelist/blacklist
- Check if the user's fingerprint is the same at registration and token validation. If not, error out explicitly.
- `fingerprint` to be defined (method, fields, TTL...)
- `check_fingerprint() -> fingerprint_errors`

---

Notes:

- Keep function calls and signatures as minimal contract. Implement validations and errors as described in the code.
- Remember to add unit tests for :
  - email validation
  - password rules
  - activation flux (tokens)

---

Modify the UML to implement user interactions. Register should be in the frontend.
Finish the implementation of the app, and have it ready for next session.

December 3:

- Session fixation? How do we mitigate this?
- Handle multiple clicks on the "token validation" link received by mail. (if already validated, then error out)

---

**Encapsulation Approach**

- **Blueprint module:** Package registration, activation, password reset, login, and logout under a dedicated blueprint (e.g., `auth_bp` with `url_prefix="/auth"`). This keeps routes, templates, and static files scoped to the module, like your existing MFA blueprint in mfa.py.
- **Service layer:** Move core flows (`register_user()`, `activate_user()`, `request_password_reset()`, `reset_password()`) into `services.py`. Routes become thin: parse input → call service → render response.
- **Repository boundary:** Access persistence via a `UserRepository` and `TokenRepository` that wrap db.py. This avoids SQL in handlers and makes the module testable.
- **Helpers:** Keep `token` generation, `email` sending (wrapping mail_handler.py), and `validators` separate from routes.
- **App factory:** Switch to `create_app()` that configures extensions and registers blueprints, so the auth module stays pluggable and reusable across apps.

**Suggested Module Structure**

- `src/auth/__init__.py`: create and export `auth_bp`.
- `src/auth/routes.py`: `/register`, `/activate/<token>`, `/forgotten_password`, `/password_reset/<token>`, `/login`, `/logout`.
- `src/auth/services.py`: `register_user(email, password)`, `activate_user(token)`, `create_reset_token(email)`, `reset_password(token, password)`.
- `src/auth/repository.py`: `UserRepository`, `TokenRepository` using db.py `get_db()`.
- `src/auth/tokens.py`: token generation + expiry windows.
- `src/auth/emails.py`: thin wrappers calling mail_handler.py.
- `src/auth/validators.py`: reuse field_utils.py and add cohesive validation utilities.
- `src/auth/templates/auth/*`: register.html, activation.html, forgotten_password.html, password_reset.html, optionally login.html.
- `src/auth/static/auth/*`: module-scoped assets if needed.

**Integration**

- **Register the blueprint:** In the app factory, `app.register_blueprint(auth_bp, url_prefix="/auth")`. Update links in shared templates to `url_for('auth.register')`, `url_for('auth.activate', token=...)`, etc. Your existing references (e.g., register.html) currently use `url_for('register')`; point them at the blueprint endpoint names.
- **App factory pattern:** Refactor app.py to:
  - Define `create_app()` that sets `SECRET_KEY`, attaches `CSRFProtect`, and registers `mfa_bp` and `auth_bp`.
  - Keep `WsgiToAsgi` wrapping in the runner section if you still use Uvicorn.
- **Dependencies:** Pass shared services via imports or light DI:
  - Database via `get_db()`.
  - CSRF via the extension (already in app.py).
  - Mail via mail_handler.py.
  - MFA remains separate (blueprint already in mfa.py); `login` route can redirect to `mfa.verify` as it does now.

**Security Boundaries**

- **Input validation:** Centralize in `validators.py` and keep templates using CSRF (`Flask-WTF` already present).
- **Password hashing:** Use `generate_password_hash` / `check_password_hash` as in app.py.
- **Token handling:** Use strong randoms, store expiry, and `used` flags (already modeled in init_db.py); wrap in `TokenRepository`.
- **Session hygiene:** Continue clearing session on login and logout; avoid coupling session keys outside the auth module.
- **Rate limiting (optional):** Add per-endpoint limits for `/register`, `/forgotten_password` to mitigate abuse.
- **Security events (optional):** Log auth-related events to `security_events` table (you already scaffolded it in init_db.py).

**Minimal Code Skeleton (illustrative)**

- `src/auth/__init__.py`

```python
from flask import Blueprint
auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")
from . import routes  # noqa: F401
```

- `src/auth/routes.py`

```python
from flask import render_template, request, url_for, redirect, session
from . import auth_bp
from . import services
from flask_wtf import csrf

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    email = request.form.get("email","")
    password = request.form.get("password","")
    confirm = request.form.get("confirm_password","")
    result = services.register_user(email, password, confirm)
    if not result.ok:
        return render_template("auth/register.html", errors=result.errors)
    return render_template("auth/register.html", email=email, mail_sent=result.mail_sent)

@auth_bp.route("/activate/<token>")
def activate(token):
    ok = services.activate_user(token)
    return render_template("auth/activation.html", success=ok), (200 if ok else 400)
```

- `src/auth/services.py`

```python
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash
from db import get_db
import field_utils
from . import emails

class Result: 
    def __init__(self, ok, errors=None, mail_sent=False): 
        self.ok = ok; self.errors = errors or []; self.mail_sent = mail_sent

def register_user(email, password, confirm):
    errors = []
    errors += field_utils.sanitize_user_input(email)
    errors += field_utils.check_email_format(email)
    errors += field_utils.check_password_strength(password)
    errors += field_utils.check_password_match(password, confirm)
    if errors: return Result(False, errors)
    db = get_db()
    try:
        db.execute(
          "INSERT INTO users (email, password_hash, created_at, activated) VALUES (?,?,?,?)",
          (email, generate_password_hash(password), datetime.now().isoformat(), 0)
        ); db.commit()
    except Exception:
        return Result(False, ["An account with this email already exists."])
    user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]
    token = secrets.token_hex(32)
    db.execute(
      "INSERT INTO tokens (token, user_id, expires_at, created_at, type) VALUES (?,?,?,?, 'activation')",
      (token, user_id, (datetime.now()+timedelta(hours=24)).isoformat(), datetime.now().isoformat())
    ); db.commit()
    mail_sent = emails.send_activation(email, token)
    return Result(True, mail_sent=mail_sent)

def activate_user(token):
    db = get_db()
    if field_utils.sanitize_user_input(token, max_len=64): return False
    row = db.execute(
      "SELECT user_id, used, expires_at FROM tokens WHERE token=? AND type='activation'", (token,)
    ).fetchone()
    if not row: return False
    user_id, used, expires_at = row[0], row[1], row[2]
    if used or datetime.now() > datetime.fromisoformat(expires_at): return False
    db.execute("UPDATE users SET activated=1 WHERE id=?", (user_id,))
    db.execute("UPDATE tokens SET used=1 WHERE token=?", (token,))
    db.commit()
    return True
```

- `src/auth/emails.py`

```python
from flask import url_for
import mail_handler

def send_activation(email, token):
    link = url_for("auth.activate", token=token, _external=True)
    try: return mail_handler.send_activation_email(email, link)
    except Exception: return False
```

**Why this keeps registration separate**

- All registration concerns live under `src/auth/*` with its own endpoints, templates, and static assets.
- The rest of the app only interacts via blueprint routes and, optionally, service APIs; there’s no direct SQL or email logic in non-auth code.
- The module can be reused across apps by registering the blueprint and providing the same `db`, CSRF, and mail dependencies.

If you want, I can scaffold `src/auth/` with this blueprint and wire it into app.py using an app factory, then migrate the registration and activation routes over while keeping existing templates working.
