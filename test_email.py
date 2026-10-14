from app.services.email_service import send_email

result = send_email(
    to_email="shaiksumiya401@gmail.com",
    subject="Hospital Appointment Email Test",
    body="This is a test email from the Hospital Appointment Booking System."
)

print("Email test result:", result)