# TODO

This file lists high-level tasks and function contracts for the login/registration/activation daemon. Each section contains the expected inputs, behavior, and returned template/result.

## Login

- Description: Handle user login.
- Inputs: email and password (hashing/verification happens server-side).
- Behavior:
  - On failure: increment `nb_failed_logins` for the user.
  - On success: reset `nb_failed_logins` and update the `last_login` timestamp.
- Signature:

```python
login(email, password) -> login_template(success)
```

## Register

- Description: Handle user registration.
- Inputs: `username`, `email`, `password`, `confirm_password`.
- Validation rules:
  - `email` must not already exist in the database.
  - `email` must be a valid format.
  - `email` must pass blacklist/whitelist checks (domain checks).
  - `password` must meet security requirements and match `confirm_password`.
- Post-action: send an activation token via email (currently printed to console in dev).
- Signature:

```python
register(username, email, password, confirm_password) -> register_template(errors, username, email)
```

## Validate Token

- Description: Activate an account using an activation token provided in an email link.
- Signature:

```python
validate_token(token) -> token_template(valid)
```

## Check Failed Logins

- Description: Check if a user exceeded the allowed number of failed login attempts and act accordingly.
- Signature / possible outcomes:

```python
check_failed_logins(userID) -> error_template(too_many_failed_logins) or rickroll
```

## Utilitarian functions

- `sanitize_user_input(value) -> sanitized_value`
- `check_password_strength(password) -> strength_errors`
- `check_email_format(email) -> email_format_errors`
- `check_email_domain(email) -> blacklist_errors | whitelist_errors`
- `update_last_login(user_id) -> None`

## Optional

- Check if the user's fingerprint is the same at registration and token validation. If not, error out explicitly.
- `fingerprint` to be defined (method, fields, TTL...)
- `check_fingerprint() -> fingerprint_errors`

## Nginx (deployment)

- Rate limiting (IP / endpoint).
- Redirection HTTP -> HTTPS. Enforced.
- Make sure static resources are exposed.

## Modify the architecture

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

December 3:

- Session fixation? How do we mitigate this?
- Handle multiple clicks on the "token validation" link received by mail. (if already validated, then error out)
