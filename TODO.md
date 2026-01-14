# TODO

This file lists high-level tasks and function contracts for the login/registration/activation daemon. Each section contains the expected inputs, behavior, and returned template/result.

## High priority / New mandatory features

**Enforce validation of the user input fields added in the new user module**

- Admin disabled accounts should receive a proper message when trying to log in.
- During the authentication flow, a user's last login date is updated before checking if the mfa is validated.

- Admin dashboard (to later validate post)
  - Delete / hide
    - posts
    - comments / ratings
    - users
    - files
    - manage user roles (admin / user / banned)

- User dashboard
  - Edit his profile (email, password, avatar)
  - View his posts / comments
  - Delete posts / account

- Documentations of the design and security decisions
  - UML diagrams (class diagram, sequence diagram for main flows)
  - Security considerations (threat model, mitigations)
  - API documentation (endpoints, request/response formats)

## Assignment check

### RBAC (Role-Based Access Control)

The system is based on distinct types of actors with different privileges and responsibilities:

- ~~Guest users (unauthenticated) – can browse public content and use keyword-based
search.~~
- Registered users (authenticated) – can add new content (including file uploads),
comment / rate posts, and delete only their own content.
- Administrators (authenticated) – can moderate the platform by deleting or managing
any content item, comment or user account.

### Optional features (extra grade)

- CSRF protection,
- Rate limiting for comments, ratings, uploads or search,
- content reporting and moderation queue (admin approval),
- security event or audit logging,
- advanced file upload hardening (image re-encoding, metadata stripping),
- security headers (CSP, X-Frame-Options, HSTS if HTTPS is enabled),
- soft-delete and restore functionality for administrators,
- optional features from previous laboratories,
- any other security-related feature proposed by the student.

---

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
