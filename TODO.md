# TODO

This file lists high-level tasks and function contracts for the login/registration/activation daemon. Each section contains the expected inputs, behavior, and returned template/result.

## Sessions management skeleton

```python
from flask import Flask, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = "clé-secrète"

app.config["SESSION_TYPE"] = "filesystem"  # ou 'sqlalchemy', 'redis', etc.
Session(app)

session["user_id"] = user["id"]
user_id = session.get("user_id")
session.clear()
```

## Login

- Description: Handle user login and create a new session, check that the user is activated (=1)
- Inputs: email and password (hashing/verification happens server-side).
- Behavior:
  - On failure: increment `nb_failed_logins` for the user.
  - On success: reset `nb_failed_logins` and update the `last_login` timestamp.
- Signature:

```python
login(email, password) -> login_template(success)
```

## Check Failed Logins

- Description: Check if a user exceeded the allowed number of failed login attempts and act accordingly.
- Signature / possible outcomes:

```python
check_failed_logins(userID) -> error_template(too_many_failed_logins) or rickroll
```

## Password Reset

- Description: Allow a user to modify his password if frogotten. The server will send the token if the mail exist in the DB.
- Signature

```python
password_reset(email) -> email_sent_if_mail_in_DB
```

## Optional features TODO

- Create a table token, with an extra column : type (registration, activation, password_reset)
- CSRF
- Rate limiting / Captcha (simple maths ? / retype something ?)
- security events logging
- MFA
- HTTPS
- Customize html error templates
- Password field copy/paste
- Fix le double welcome link sur le register
- Session Fixation, when login create a new session
- utiliser app.logger.exception("test") plutôt que de réimporter logging ?0

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

## Chore for a cleaner project

- Move all the functions to utils.py
- Create a src folder and copy only this one to the container
- Try to use less templates in .html and use more place holders

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
