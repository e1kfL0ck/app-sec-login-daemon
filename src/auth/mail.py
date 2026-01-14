"""
Email sending utilities for auth module.
Handles SMTP configuration, email delivery, and Flask integration.
"""

import os
import logging

import smtplib
import ssl
from email.message import EmailMessage

from flask import url_for

# Set up logging
debug_mode = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
if debug_mode:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:     %(name)s - %(message)s",
    )

# Read mail configuration from environment variables
mail_username = os.environ.get("MAIL_USERNAME")
mail_password = os.environ.get("MAIL_PASSWORD")
mail_from = os.environ.get("MAIL_FROM", mail_username)
smtp_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
smtp_port = int(os.environ.get("MAIL_PORT", 587))


def _send_email(subject: str, to_email: str, text_body: str, html_body: str) -> bool:
    """
    Internal function to send email via SMTP.
    Returns True on success, False on failure.
    """
    if not mail_username or not mail_password:
        logger.warning(
            "Mail credentials not configured; skipping email to %s",
            to_email,
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = to_email

    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            # Use STARTTLS for port 587
            if smtp_port == 587:
                server.starttls(context=context)
                server.ehlo()
            server.login(mail_username, mail_password)
            server.send_message(msg)
            logger.info("Email sent to %s", to_email)
            return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def send_activation_email(email: str, token: str) -> bool:
    """
    Send account activation email to user.
    Returns True if mail was sent, False otherwise.
    """
    activation_link = url_for("auth.activate", token=token, _external=True)

    text_body = (
        f"Hello,\n\n"
        f"Please activate your account by clicking the link below:\n\n{activation_link}\n\n"
        "If you didn't request this, you can safely ignore this email.\n"
    )

    html_body = f"""
    <html>
      <body>
        <p>Hello,</p>
        <p>Please activate your account by clicking the link below:</p>
        <p><a href="{activation_link}">Activate account</a></p>
        <p>If you didn't request this, you can safely ignore this email.</p>
      </body>
    </html>
    """

    try:
        return _send_email(
            subject="Activate your account - AppSec",
            to_email=email,
            text_body=text_body,
            html_body=html_body,
        )
    except Exception:
        logger.exception("Error preparing activation email for %s", email)
        return False


def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email to user.
    Returns True if mail was sent, False otherwise.
    """
    reset_link = url_for("auth.password_reset", token=token, _external=True)

    text_body = (
        f"Hello,\n\n"
        f"Please reset your password by clicking the link below:\n\n{reset_link}\n\n"
        "If you didn't request this, you can safely ignore this email.\n"
    )

    html_body = f"""
    <html>
      <body>
        <p>Hello,</p>
        <p>Please reset your password by clicking the link below:</p>
        <p><a href="{reset_link}">Reset password</a></p>
        <p>If you didn't request this, you can safely ignore this email.</p>
      </body>
    </html>
    """

    try:
        return _send_email(
            subject="Reset your password - AppSec",
            to_email=email,
            text_body=text_body,
            html_body=html_body,
        )
    except Exception:
        logger.exception("Error preparing password reset email for %s", email)
        return False
