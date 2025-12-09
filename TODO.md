# TODO

This file lists high-level tasks and function contracts for the login/registration/activation daemon. Each section contains the expected inputs, behavior, and returned template/result.

## Urgent

- It seems some kind of user data remains in the database when restarting the app, altough init_db is set to true. Why is that? (upon login, the old session is still valid, altough the account doesn't exist?)
- Implement a mitigation to prevent password-reset mail requests spam
- Implement a mitigation to prevent bruteforce on 2FA? (or test if by default it works)
- Add documentation for MFA (docstring)
- Prevent injection on MFA, by using already implemented utils.
- Expire activation token upon use. (mail account activation)

## Optional features TODO

- Create a table token, with an extra column : type (registration, activation, password_reset)
- CSRF ok, a mettre ds le header
- Rate limiting / Captcha (simple maths ? / retype something ?)
- security events logging
- MFA
- HTTPS
- Customize html error templates
- Session Fixation, when login create a new session
- utiliser app.logger.exception("test") plutôt que de réimporter logging ?
- le temps du mail est trop rapide si mauvais mail
- keep the user from going backward into the 2FA process (or even better, make it so that once enrolled, the user doesn't have access to the MFA anymore, unless he gets a token by email - like password reset)

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
