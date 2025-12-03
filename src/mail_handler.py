import os
import logging

import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(name)s - %(message)s",
)


def send_activation_email(to_email: str, activation_link: str) -> bool:
    """
    Send an activation email using SMTP. Returns True on success, False on failure.

    Configuration is read from environment variables:
    - MAIL_USERNAME: SMTP username (required)
    - MAIL_PASSWORD: SMTP password or app password (required)
    - MAIL_FROM: optional from address (defaults to MAIL_USERNAME)
    - MAIL_SERVER: optional SMTP server (defaults to smtp.gmail.com)
    - MAIL_PORT: optional SMTP port (defaults to 587)
    """
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_from = os.environ.get("MAIL_FROM", mail_username)
    smtp_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("MAIL_PORT", 587))

    if not mail_username or not mail_password:
        logger.warning(
            "Mail credentials not configured; skipping sending activation email to %s",
            to_email,
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = "Activate your account - AppSec"
    msg["From"] = mail_from
    msg["To"] = to_email

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
        <p><a href=\"{activation_link}\">Activate account</a></p>
        <p>If you didn't request this, you can safely ignore this email.</p>
      </body>
    </html>
    """

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
            logger.info("Activation email sent to %s", to_email)
            return True
    except Exception:
        logger.exception("Failed to send activation email to %s", to_email)
        return False
