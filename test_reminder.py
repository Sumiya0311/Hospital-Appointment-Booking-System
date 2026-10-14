from app.services.reminder_service import send_appointment_reminders

if __name__ == "__main__":
    print("Starting appointment reminder test...")
    send_appointment_reminders()
    print("Reminder job finished. Check Mailtrap.")