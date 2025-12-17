# Auth Module - Quick Reference

## Files Created/Modified

### New Files

```bash
src/auth/__init__.py           ← Blueprint definition
src/auth/services.py            ← Business logic layer
src/auth/repository.py          ← Data access layer
src/auth/validators.py          ← Input validation
src/auth/tokens.py              ← Token utilities
src/auth/emails.py              ← Email wrappers
AUTH_MODULE_STRUCTURE.md        ← Detailed documentation
CONTENT_MODULE_EXAMPLE.md       ← Example for extending
```

### Modified Files

```bash
src/auth/routes.py              ← Refactored to use services
src/app.py                      ← Already imports auth_bp
```

## Architecture Diagram

```bash
┌─────────────────────────────────────────────────────┐
│                   routes.py                         │
│  GET/POST handlers, request/response, redirects     │
└──────────┬──────────────────────────────────────────┘
           │ calls
           ▼
┌─────────────────────────────────────────────────────┐
│                   services.py                       │
│  Business logic, workflows, validation              │
├──────────────────────────────────────────────────────┤
│ • register_user()                                    │
│ • login_user()                                       │
│ • activate_user()                                    │
│ • request_password_reset()                           │
│ • reset_password()                                   │
└──────────┬──────────────────────────────────────────┘
           │ uses
           ▼
┌─────────────────────────────────────────────────────┐
│         repository.py  validators.py  tokens.py     │
│         emails.py                                    │
├──────────────────────────────────────────────────────┤
│ • UserRepository (CRUD)                              │
│ • TokenRepository (token management)                 │
│ • Input validation                                   │
│ • Token generation & expiry                          │
│ • Email sending wrappers                             │
└──────────┬──────────────────────────────────────────┘
           │ uses
           ▼
┌─────────────────────────────────────────────────────┐
│      db.py  field_utils.py  mail_handler.py         │
│        session_helpers.py                            │
│ (Shared infrastructure)                              │
└─────────────────────────────────────────────────────┘
```

## Key Functions Reference

### Services API

```python
# Registration
result = services.register_user(email, password, confirm_password)
# → RegistrationResult(ok: bool, errors: list, mail_sent: bool)

# Activation
ok = services.activate_user(token)
# → bool

# Login
login_result = services.login_user(email, password)
# → LoginResult(ok: bool, user_id: int, error_msg: str, require_reset: bool, mfa_enabled: bool)

# Password Reset Flow
reset_result = services.request_password_reset(email)
# → RegistrationResult(ok: bool, errors: list, mail_sent: bool)

user_id = services.validate_password_reset_token(token)
# → user_id or None

ok, errors = services.reset_password(token, password, confirm_password)
# → (bool, list)
```

### Repository API

```python
# Users
user_id = UserRepository.create(email, password_hash)
user_tuple = UserRepository.get_by_email(email)
user_tuple = UserRepository.get_by_id(user_id)
UserRepository.activate(user_id)
UserRepository.increment_failed_logins(user_id)
UserRepository.reset_failed_logins(user_id)
UserRepository.update_last_login(user_id)
UserRepository.update_password(user_id, password_hash)

# Tokens
TokenRepository.create(token, user_id, expires_at, token_type)
token_tuple = TokenRepository.get_by_token(token, token_type)  # (user_id, used, expires_at)
TokenRepository.mark_used(token)
TokenRepository.invalidate_all_of_type_for_user(user_id, token_type)
```

## Template Variables

### register.html

```django
{{ errors|list }}              ← Form validation errors
{{ email }}                    ← Pre-filled email
{{ mail_sent|bool }}           ← Success message condition
```

### activation.html

```django
{{ success|bool }}             ← Success/failure flag
```

### login.html

```django
{{ errors|bool }}              ← Show error message
{{ reset|bool }}               ← Show password reset prompt
```

### password_reset.html

```django
{{ token }}                    ← Hidden token field
{{ errors|list }}              ← Validation errors
{{ success|bool }}             ← Success message
```

### forgotten_password.html

```django
{{ email }}                    ← Pre-filled email
{{ mail_sent|bool }}           ← Success message
```

## Security Checklist

- ✅ Input validation (sanitization, length, format)
- ✅ Password hashing (werkzeug.security)
- ✅ Token security (64-char hex, expiry)
- ✅ Session management (clear on login)
- ✅ Brute force protection (failed login tracking)
- ✅ Email enumeration prevention (consistent responses)
- ✅ MFA integration (pre_auth_user_id flow)
- ✅ CSRF protection (Flask-WTF)
- ⏳ Rate limiting (optional, can be added)
- ⏳ Audit logging (optional, can be added)

## Adding a New Auth Feature

Example: Add "change password" endpoint

```python
# 1. Add to validators.py
def validate_change_password_input(current_password, new_password, confirm_password):
    errors = []
    if not current_password:
        errors.append("Current password required.")
    errors += fu.check_password_strength(new_password)
    errors += fu.check_password_match(new_password, confirm_password)
    return errors

# 2. Add to services.py
def change_password(user_id, current_password, new_password, confirm_password):
    errors = validators.validate_change_password_input(...)
    if errors:
        return (False, errors)
    
    user = UserRepository.get_by_id(user_id)
    if not check_password_hash(user[2], current_password):  # user[2] is password_hash
        return (False, ["Current password is incorrect."])
    
    password_hash = generate_password_hash(new_password)
    UserRepository.update_password(user_id, password_hash)
    return (True, None)

# 3. Add route in routes.py
@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    
    current = request.form.get("current_password", "")
    new = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")
    
    ok, errors = services.change_password(session["user_id"], current, new, confirm)
    if not ok:
        return render_template("change_password.html", errors=errors)
    
    return render_template("change_password.html", success=True)

# 4. Add template: src/auth/templates/change_password.html
```

## Testing Examples

```python
# Test registration
result = services.register_user("user@example.com", "Password123!", "Password123!")
assert result.ok == True
assert result.mail_sent == True

# Test login
login_result = services.login_user("user@example.com", "Password123!")
assert login_result.ok == False  # Not activated yet

# Test activation
ok = services.activate_user(activation_token)
assert ok == True

# Now login should work
login_result = services.login_user("user@example.com", "Password123!")
assert login_result.ok == True
assert login_result.user_id > 0
```

## Common Patterns

### Check if user is logged in

```python
@login_required
def protected_route():
    user_id = session.get("user_id")
    # ...
```

### Check if user is NOT logged in

```python
@already_logged_in
def register():
    # Only allow unauthenticated users
    # ...
```

### Handle errors in forms

```python
if request.method == "POST":
    result = services.some_operation(...)
    if not result.ok:
        return render_template("form.html", errors=result.errors)
    return render_template("form.html", success=True)
```

### Prevent email enumeration

```python
# Always return success, even if user doesn't exist
result = services.request_password_reset(email)
return render_template("template.html", mail_sent=result.mail_sent)
```

---

For detailed documentation, see:

- `AUTH_MODULE_STRUCTURE.md` - Full design documentation
- `CONTENT_MODULE_EXAMPLE.md` - Example of extending with content module
