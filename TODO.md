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
