## TODO

This file lists high-level tasks and function contracts for the login/registration/activation daemon. Each section contains the expected inputs, behavior, and returned template/result.

### Login

- Description: Handle user login.
- Inputs: email and password (hashing/verification happens server-side).
- Behavior:
    - On failure: increment `nb_failed_logins` for the user.
    - On success: reset `nb_failed_logins` and update the `last_login` timestamp.
- Signature:

```
login(email, password) -> login_template(success)
```

### Register

- Description: Handle user registration.
- Inputs: `username`, `email`, `password`, `confirm_password`.
- Validation rules:
    - `email` must not already exist in the database.
    - `email` must be a valid format.
    - `email` must pass blacklist/whitelist checks (domain checks).
    - `password` must meet security requirements and match `confirm_password`.
- Post-action: send an activation token via email (currently printed to console in dev).
- Signature:

```
register(username, email, password, confirm_password) -> register_template(errors, username, email)
```

### Validate Token

- Description: Activate an account using an activation token provided in an email link.
- Signature:

```
validate_token(token) -> token_template(valid)
```

### Check Failed Logins

- Description: Check if a user exceeded the allowed number of failed login attempts and act accordingly.
- Signature / possible outcomes:

```
check_failed_logins(userID) -> error_template(too_many_failed_logins) or rickroll
```

### Fonctions utilitaires

- `sanitize_user_input(value) -> sanitized_value`
- `check_password_strength(password) -> strength_errors`
- `check_email_format(email) -> email_format_errors`
- `check_email_domain(email) -> blacklist_errors | whitelist_errors`
- `update_last_login(user_id) -> None`

### Optionnel

- Vérifier si l'empreinte du navigateur (browser fingerprint) est la même entre l'enregistrement et la validation du token.
- `fingerprint` : à déterminer (méthode, fields, TTL, stockage).
- `check_browser_fingerprint() -> fingerprint_errors`

### Nginx (déploiement)

- Rate limiting (limiter tentatives par IP / endpoint).
- Redirection HTTP -> HTTPS.
- Exposer correctement les ressources statiques (`/static`).

---

Notes:
- Garder les signatures de fonctions comme contrat minimal. Implémenter validations et erreurs détaillées dans le code.
- Penser à ajouter tests unitaires pour :
    - validation d'email
    - règles de mot de passe
    - flux d'activation (token)


