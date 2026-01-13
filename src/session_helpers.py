from flask import session, redirect, url_for
from functools import wraps


# Ensure the user is logged in
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def already_logged_in(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped
