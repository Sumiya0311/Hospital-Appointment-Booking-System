import smtplib
from email.message import EmailMessage

from app.config import settings


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME:
        print("Email not sent: SMTP settings are missing.")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as server:
            server.starttls()
            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )
            server.send_message(message)

        print(f"Email sent successfully to {to_email}")
        return True

    except (smtplib.SMTPException, OSError) as exc:
        print(f"Email delivery failed: {exc}")
        return False