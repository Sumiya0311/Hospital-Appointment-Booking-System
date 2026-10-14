from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.department import router as department_router
from app.routers.doctor import router as doctor_router
from app.routers.schedule import router as schedule_router
from app.routers.leave import router as leave_router
from app.routers.appointment import router as appointment_router
from app.routers.history import router as history_router
from app.routers.consultation import router as consultation_router
from app.routers.file import router as file_router
from app.routers.queue import router as queue_router
from app.services.scheduler import start_scheduler, stop_scheduler
from app.routers.report import router as report_router
from app.routers.queue import router as queue_router
from app.websockets.queue import router as ws_queue_router
from app.services.scheduler import start_scheduler, stop_scheduler
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    print("Appointment reminder scheduler started.")
    try:
        yield
    finally:
        stop_scheduler()
        print("Appointment reminder scheduler stopped.")


app = FastAPI(
    title="Hospital Appointment Booking System",
    description=(
        "Hospital backend with authentication, doctor schedules, "
        "appointments, consultations, medical files, live queue, "
        "history, and scheduled reminders."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(auth_router)
app.include_router(department_router)
app.include_router(doctor_router)
app.include_router(schedule_router)
app.include_router(leave_router)
app.include_router(appointment_router)
app.include_router(history_router)
app.include_router(consultation_router)
app.include_router(file_router)
app.include_router(queue_router)
app.include_router(report_router)
app.include_router(queue_router)
app.include_router(ws_queue_router)


@app.get("/", tags=["Health"])
def home():
    return {
        "message": "Hospital Appointment Booking System is running",
        "status": "healthy",
    }