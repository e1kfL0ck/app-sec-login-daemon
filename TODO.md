"""
    Login: Handles user login functionality.
        Input email and password hash and check against the database.
        if fail, nb_failed_logins is incremented.
        if success, reset nb_failed_logins and update last_login timestamp.
"""
login(email, password) -> login_template(success)


"""
    Register: Handles user registration functionality.
        Input username, email, password and confirm password, validate them and store in the database.
        email must not exist already.
        email must be valid format.
        email must be in blacklist/whitelist.
        Password must match security requirements.
        Send an email with an activation token. (in the console)
"""
register(username, email, password, confirm_password) -> register_template(errors, username, email)

"""
    Validate Token: Handles account activation via token.
        Input token from email link, validate it and activate the user account.
"""
validate_token(token) -> token_template(valid)

"""
    Check Failed Logins: Checks if a user has exceeded the allowed number of failed login attempts
"""
check_failed_logins(userID) -> error_template(too_many_failed_logins) or rickroll


Fonction utils :

sanitize_user_input(value) -> sanitized_value

check_password_strength(password) -> strength_errors

check_email_format(email) -> email_format_errors

check_email_domain(email) -> blacklist_errors or whitelist_errors

update_last_login(user_id) -> None


Optional :

"""
    Check if it's the same fingerprint between registration and token validation
    fingerprint : to be determined
"""
check_browser_fingerprint() -> fingerprint_errors


Nginx :
Rate Limiting
http to https redirection
Expose static ressources

