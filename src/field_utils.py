import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

DANGEROUS_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # onclick=, onerror=, etc.
    re.compile(r"javascript\s*:", re.IGNORECASE),
]

DISALLOWED_CHARS = set("<>{};&")


def check_password_match(password: str, confirm_password: str) -> list[str]:
    errors = []
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors


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
