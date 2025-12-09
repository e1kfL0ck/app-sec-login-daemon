from flask import Blueprint, render_template, request, session, redirect, url_for
import pyotp
import qrcode
import io
import base64
import json
import secrets

# custom imports
import field_utils
from db import get_db

mfa_bp = Blueprint("mfa", __name__, url_prefix="/mfa")


@mfa_bp.before_request
def _require_login_for_mfa():
    # allow pre-auth flow for verify route (when coming from login)
    if "user_id" not in session and "pre_auth_user_id" not in session:
        return redirect(url_for("login", next=request.path))


@mfa_bp.after_request
def _no_cache(response):
    # Prevent caching of MFA pages
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _qr_datauri(provisioning_uri):
    img = qrcode.make(provisioning_uri)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@mfa_bp.route("/setup", methods=["GET"])
def setup():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_email = session.get("email")
    secret = pyotp.random_base32()
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email, issuer_name="AppSec"
    )
    qr = _qr_datauri(provisioning_uri)
    return render_template("mfa_setup.html", secret=secret, qr=qr)


@mfa_bp.route("/confirm", methods=["POST"])
def confirm():
    if "user_id" not in session:
        return redirect(url_for("login"))
    secret = request.form.get("secret", "")
    code = request.form.get("otp", "")

    errors = []
    errors += field_utils.sanitize_user_input(secret)
    errors += field_utils.sanitize_user_input(code)
    if errors:
        return render_template(
            "mfa_setup.html", error="Secret or code invalid", secret=secret
        )

    if not secret or not code:
        return render_template("mfa_setup.html", error="Missing fields", secret=secret)

    user_id = session["user_id"]
    if pyotp.TOTP(secret).verify(code, valid_window=1):
        db = get_db()
        backup_codes = [secrets.token_hex(6) for _ in range(8)]
        db.execute(
            "UPDATE users SET mfa_enabled = 1, mfa_secret = ?, backup_codes = ? WHERE id = ?",
            (secret, json.dumps(backup_codes), user_id),
        )
        db.commit()
        return render_template(
            "activation.html", mfa_success=True, backup_codes=backup_codes
        )
    return render_template("mfa_setup.html", error="Invalid code", secret=secret)


@mfa_bp.route("/verify", methods=["GET", "POST"])
def verify():
    # Called when session is in pre-auth state (session['pre_auth_user_id'])
    if request.method == "GET":
        return render_template("mfa_verify.html")
    
    code = request.form.get("otp", "")
    user_id = session.get("pre_auth_user_id")
    if not user_id:
        return redirect(url_for("login"))
    # TODO: is this needed? @emile
    # errors = []
    # errors += field_utils.sanitize_user_input(code)
    # if errors:
    #     return render_template("mfa_verify.html", error="Code invalid")
    db = get_db()
    row = db.execute(
        "SELECT email, mfa_secret, backup_codes FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    if not row:
        return redirect(url_for("login"))
    email, secret, backup_json = row
    if secret and pyotp.TOTP(secret).verify(code, valid_window=1):
        # login finalization
        session.clear()
        session["user_id"] = user_id
        session["email"] = email
        return redirect(url_for("dashboard"))

    # TODO: what's that? @emile
    # check backup codes
    # if backup_json:
    #     backups = json.loads(backup_json)
    #     if code in backups:
    #         backups.remove(code)
    #         db.execute("UPDATE users SET backup_codes = ? WHERE id = ?", (json.dumps(backups), user_id))
    #         db.commit()
    #         session.clear()
    #         session["user_id"] = user_id
    #         email = db.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    #         session["email"] = email
    #         return redirect(url_for("dashboard"))
    return render_template("mfa_verify.html", error="Invalid code"), 400
