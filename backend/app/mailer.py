"""Send one plain-text email. SMTP when SMTP_HOST is set, otherwise only log it."""

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

log = logging.getLogger("studeal.mail")


def _send_smtp(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)


async def send_email(to: str, subject: str, body: str) -> bool:
    """True if the email went out (or was logged because SMTP is off)."""
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    if not settings.smtp_host:
        log.warning("SMTP is off, email not sent. To: %s | %s\n%s", to, subject, body)
        print(f"[email] to={to} subject={subject}\n{body}", flush=True)
        return True
    try:
        await asyncio.to_thread(_send_smtp, message)
    except OSError, smtplib.SMTPException:
        log.exception("Could not send email to %s", to)
        return False
    return True
