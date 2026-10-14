from app.services.email_service import send_email


def main():
    print("Starting reminder email test...")

    recipient = "shaiksumiya401@gmail.com"

    subject = "Hospital Appointment Reminder Test"

    body = (
        "Hello,\n\n"
        "This is a test email for the Hospital Appointment Booking System.\n\n"
        "Email delivery through SMTP is being tested successfully.\n\n"
        "Thank you."
    )

    result = send_email(
        to_email=recipient,
        subject=subject,
        body=body,
    )

    print(f"Email test result: {result}")

    if result:
        print("Email accepted by the SMTP server. Check Mailtrap.")
    else:
        print("Email was not sent. Check the SMTP error in the terminal.")


if __name__ == "__main__":
    main()