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
    session["mfa_setup_secret"] = secret
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email, issuer_name="AppSec"
    )
    qr = _qr_datauri(provisioning_uri)
    return render_template("mfa_setup.html", qr=qr, secret=secret)


"""
Handle MFA confirmation and setup completion.

This route processes the OTP code submitted by the user during MFA setup.
It verifies the code against the temporary secret stored in the session,
and if valid, enables MFA for the user and generates backup codes.

Returns:
    Response: Redirects to login if user is not authenticated.
              Renders mfa_setup.html with error message if:
                - OTP code contains invalid characters
                - Secret or code is missing
                - OTP code verification fails
              Renders activation.html with success message and backup codes
              if MFA setup is successful.

Notes:
    - Expects 'user_id' and 'mfa_setup_secret' in session
    - Expects 'otp' field in POST form data
    - Uses valid_window=1 for TOTP verification (30-second tolerance)
    - Generates 8 backup codes (12 character hex strings)
    - Stores backup codes as JSON in database
"""
@mfa_bp.route("/confirm", methods=["POST"])
def confirm():
    if "user_id" not in session:
        return redirect(url_for("login"))

    code = request.form.get("otp", "")
    errors = []
    errors += field_utils.sanitize_user_input(code)

    secret = session.get("mfa_setup_secret", "")

    if errors:
        return render_template("mfa_setup.html", error="Secret code invalid")

    #TODO: if not secret, it should be regenerate trought @mfa_bp.route("/setup", methods=["GET"])
    if not secret or not code:
        return render_template("mfa_setup.html", error="Missing fields")

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


"""
Handle MFA verification for users in pre-authentication state.

This route handles both GET and POST requests for MFA verification:
- GET: Displays the MFA verification form
- POST: Verifies the submitted OTP code or backup code

The function checks the user's TOTP secret or backup codes to authenticate.
Upon successful verification, the user is logged in and redirected to the dashboard.

Returns:
    GET: Rendered template for MFA verification form
    POST (success): Redirect to dashboard after successful verification
    POST (failure): Rendered template with error message and 400 status code

Redirects:
    - To login page if no pre_auth_user_id in session or user not found
    - To dashboard after successful MFA verification

Session Requirements:
    - pre_auth_user_id: User ID set during initial login before MFA verification

Session Updates:
    On successful verification:
    - Clears pre-authentication session data
    - Sets user_id and email in session

Notes:
    - TOTP codes are verified with a valid_window of 1 (allows ±30 seconds)
    - Backup codes are single-use and removed after successful verification
    - Used backup codes trigger a database update to remove them from the list
"""
@mfa_bp.route("/verify", methods=["GET", "POST"])
def verify():
    # Called when session is in pre-auth state (session['pre_auth_user_id'])
    if request.method == "GET":
        return render_template("mfa_verify.html")

    code = request.form.get("otp", "")
    user_id = session.get("pre_auth_user_id")
    if not user_id:
        return redirect(url_for("login"))
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
        #TODO: update last login
        return redirect(url_for("dashboard"))

    if backup_json:
        backups = json.loads(backup_json)
        if code in backups:
            backups.remove(code)
            db.execute("UPDATE users SET backup_codes = ? WHERE id = ?", (json.dumps(backups), user_id))
            db.commit()
            session.clear()
            session["user_id"] = user_id
            email = db.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()[0]
            session["email"] = email
            #TODO: update last login
            return redirect(url_for("dashboard"))
        
    #TODO: increment failed logins
    return render_template("mfa_verify.html", error="Invalid code"), 400
