from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.appointment import Appointment
from app.models.user import User
from app.services.email_service import send_email


def send_appointment_reminders():
    db: Session = SessionLocal()

    try:
        tomorrow = date.today() + timedelta(days=1)

        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.appointment_date == tomorrow,
                Appointment.status == "Booked",
                Appointment.reminder_sent == False,
            )
            .all()
        )

        print(f"Appointments found for reminder: {len(appointments)}")

        for appointment in appointments:
            patient = (
                db.query(User)
                .filter(User.id == appointment.patient_id)
                .first()
            )

            if not patient or not patient.email:
                print(
                    f"No patient email for appointment {appointment.id}"
                )
                continue

            subject = "Hospital Appointment Reminder"
            body = (
                f"Hello {patient.name},\n\n"
                "This is a reminder for your hospital appointment.\n"
                f"Appointment number: {appointment.appointment_number}\n"
                f"Date: {appointment.appointment_date}\n"
                f"Time: {appointment.slot_time}\n"
                f"Queue token: {appointment.token_number}\n\n"
                "Please arrive on time.\n"
                "Thank you."
            )

            sent = send_email(patient.email, subject, body)
            print(f"Reminder email result for appointment "
                  f"{appointment.id}: {sent}")

            if sent:
                appointment.reminder_sent = True

        db.commit()

    except Exception as exc:
        db.rollback()
        print(f"Reminder job failed: {exc}")

    finally:
        db.close()