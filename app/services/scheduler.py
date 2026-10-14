from apscheduler.schedulers.background import BackgroundScheduler

from app.services.reminder_service import send_appointment_reminders

scheduler = BackgroundScheduler()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            send_appointment_reminders,
            trigger="cron",
            hour=9,
            minute=0,
            id="appointment_reminders",
            replace_existing=True,
        )
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)