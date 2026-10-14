from datetime import date, datetime, time, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.leave import DoctorLeave
from app.models.schedule import DoctorSchedule
from app.models.history import AppointmentHistory
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.routers.queue import manager
from app.services.email_service import send_email


router = APIRouter(prefix="/appointments", tags=["Appointments"])


def send_appointment_email(
    recipient: str | None,
    subject: str,
    body: str,
):
    """Send an email without interrupting the appointment operation."""
    if not recipient:
        print("Appointment email skipped: recipient email is missing.")
        return

    try:
        result = send_email(
            to_email=recipient,
            subject=subject,
            body=body,
        )
        print("Appointment email result:", result)
    except Exception as error:
        print("Appointment email error:", repr(error))


def validate_future_date(appointment_date: date):
    today = date.today()

    if appointment_date < today:
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past.",
        )

    if appointment_date > today + timedelta(days=30):
        raise HTTPException(
            status_code=400,
            detail="Appointments can only be booked within the next 30 days.",
        )


def validate_schedule(
    db: Session,
    doctor: Doctor,
    appointment_date: date,
    slot_time: time,
):
    if not getattr(doctor, "is_active", True):
        raise HTTPException(status_code=400, detail="Doctor is not active.")

    leave = (
        db.query(DoctorLeave)
        .filter(
            DoctorLeave.doctor_id == doctor.id,
            DoctorLeave.leave_date == appointment_date,
        )
        .first()
    )

    if leave:
        raise HTTPException(
            status_code=400,
            detail="Doctor is on leave on this date.",
        )

    schedule = (
        db.query(DoctorSchedule)
        .filter(
            DoctorSchedule.doctor_id == doctor.id,
            DoctorSchedule.day_of_week == appointment_date.weekday(),
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=400,
            detail="Doctor has no schedule for this day.",
        )

    start_time = schedule.start_time
    end_time = schedule.end_time

    if slot_time < start_time or slot_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="Appointment time is outside the doctor's working hours.",
        )

    break_start = getattr(schedule, "break_start", None)
    break_end = getattr(schedule, "break_end", None)

    if (
        break_start
        and break_end
        and break_start <= slot_time < break_end
    ):
        raise HTTPException(
            status_code=400,
            detail="Appointment time falls within the doctor's break.",
        )

    duration = getattr(doctor, "slot_duration", 15) or 15
    slot_minutes = slot_time.hour * 60 + slot_time.minute
    start_minutes = start_time.hour * 60 + start_time.minute

    if (slot_minutes - start_minutes) % duration != 0:
        raise HTTPException(
            status_code=400,
            detail=f"Appointments must start at {duration}-minute intervals.",
        )


def add_history(
    db: Session,
    appointment: Appointment,
    old_status: str | None,
    new_status: str,
    changed_by: int,
):
    history = AppointmentHistory(
        appointment_id=appointment.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(history)


def check_slot_conflict(
    db: Session,
    doctor_id: int,
    appointment_date: date,
    slot_time: time,
    exclude_appointment_id: int | None = None,
):
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.slot_time == slot_time,
        Appointment.status == "Booked",
    )

    if exclude_appointment_id is not None:
        query = query.filter(Appointment.id != exclude_appointment_id)

    if query.first():
        raise HTTPException(
            status_code=409,
            detail="This appointment slot is already booked. Please choose another slot.",
        )


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can book appointments.",
        )

    validate_future_date(payload.appointment_date)

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == payload.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    validate_schedule(
        db,
        doctor,
        payload.appointment_date,
        payload.slot_time,
    )

    patient_conflict = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == current_user.id,
            Appointment.appointment_date == payload.appointment_date,
            Appointment.slot_time == payload.slot_time,
            Appointment.status == "Booked",
        )
        .first()
    )

    if patient_conflict:
        raise HTTPException(
            status_code=409,
            detail="You already have an appointment at this date and time.",
        )

    check_slot_conflict(
        db,
        doctor.id,
        payload.appointment_date,
        payload.slot_time,
    )

    try:
        max_token = (
            db.query(Appointment.token_number)
            .filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == payload.appointment_date,
            )
            .order_by(Appointment.token_number.desc())
            .first()
        )

        token_number = (max_token[0] if max_token else 0) + 1
        now = datetime.now()

        appointment = Appointment(
            appointment_number=f"APT-{uuid4().hex[:12].upper()}",
            patient_id=current_user.id,
            doctor_id=doctor.id,
            appointment_date=payload.appointment_date,
            slot_time=payload.slot_time,
            token_number=token_number,
            reason=payload.reason,
            status="Booked",
            consultation_fee=doctor.consultation_fee,
            reschedule_count=0,
            reminder_sent=False,
            created_at=now,
            updated_at=now,
        )

        db.add(appointment)
        db.flush()

        add_history(
            db,
            appointment,
            None,
            "Booked",
            current_user.id,
        )

        db.commit()
        db.refresh(appointment)

        # Booking confirmation email
        send_appointment_email(
            recipient=getattr(current_user, "email", None),
            subject="Appointment Booking Confirmation",
            body=(
                "Dear Patient,\n\n"
                "Your hospital appointment has been booked successfully.\n\n"
                f"Appointment Number: {appointment.appointment_number}\n"
                f"Doctor ID: {appointment.doctor_id}\n"
                f"Date: {appointment.appointment_date}\n"
                f"Time: {appointment.slot_time}\n"
                f"Token Number: {appointment.token_number}\n"
                f"Status: {appointment.status}\n\n"
                "Thank you for choosing our hospital."
            ),
        )

        try:
            await manager.broadcast(
                doctor.id,
                {
                    "event": "appointment_booked",
                    "appointment_id": appointment.id,
                    "token_number": appointment.token_number,
                    "appointment_date": str(appointment.appointment_date),
                    "slot_time": str(appointment.slot_time),
                },
            )
        except Exception as websocket_error:
            print("WebSocket notification error:", repr(websocket_error))

        return appointment

    except IntegrityError as error:
        db.rollback()
        print("APPOINTMENT INTEGRITY ERROR:", repr(error.orig))
        raise HTTPException(
            status_code=409,
            detail=f"Database constraint error: {error.orig}",
        )

    except SQLAlchemyError as error:
        db.rollback()
        print("APPOINTMENT DATABASE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Database error while booking the appointment.",
        )


@router.get("/my", response_model=list[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can view this endpoint.",
        )

    return (
        db.query(Appointment)
        .filter(Appointment.patient_id == current_user.id)
        .order_by(
            Appointment.appointment_date,
            Appointment.slot_time,
        )
        .all()
    )


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    if (
        current_user.role != "Admin"
        and appointment.patient_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot cancel this appointment.",
        )

    if appointment.status != "Booked":
        raise HTTPException(
            status_code=400,
            detail="Only booked appointments can be cancelled.",
        )

    old_status = appointment.status
    appointment.status = "Cancelled"
    appointment.updated_at = datetime.now()

    add_history(
        db,
        appointment,
        old_status,
        "Cancelled",
        current_user.id,
    )

    try:
        db.commit()
        db.refresh(appointment)
    except SQLAlchemyError as error:
        db.rollback()
        print("CANCELLATION DATABASE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Database error while cancelling the appointment.",
        )

    # Cancellation email
    patient = appointment.patient
    send_appointment_email(
        recipient=getattr(patient, "email", None),
        subject="Appointment Cancellation Confirmation",
        body=(
            "Dear Patient,\n\n"
            "Your hospital appointment has been cancelled.\n\n"
            f"Appointment Number: {appointment.appointment_number}\n"
            f"Date: {appointment.appointment_date}\n"
            f"Time: {appointment.slot_time}\n"
            f"Status: {appointment.status}\n\n"
            "Please contact the hospital if you need assistance."
        ),
    )

    try:
        await manager.broadcast(
            appointment.doctor_id,
            {
                "event": "appointment_cancelled",
                "appointment_id": appointment.id,
                "token_number": appointment.token_number,
            },
        )
    except Exception as websocket_error:
        print("WebSocket notification error:", repr(websocket_error))

    return {
        "message": "Appointment cancelled successfully.",
        "appointment_id": appointment.id,
        "status": appointment.status,
    }


@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int,
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    if (
        current_user.role != "Patient"
        or appointment.patient_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot reschedule this appointment.",
        )

    if appointment.status != "Booked":
        raise HTTPException(
            status_code=400,
            detail="Only booked appointments can be rescheduled.",
        )

    if appointment.reschedule_count >= 2:
        raise HTTPException(
            status_code=400,
            detail="Maximum reschedule limit reached.",
        )

    if payload.doctor_id != appointment.doctor_id:
        raise HTTPException(
            status_code=400,
            detail="Rescheduling to another doctor is not supported.",
        )

    validate_future_date(payload.appointment_date)

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == appointment.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    validate_schedule(
        db,
        doctor,
        payload.appointment_date,
        payload.slot_time,
    )

    check_slot_conflict(
        db,
        doctor.id,
        payload.appointment_date,
        payload.slot_time,
        exclude_appointment_id=appointment.id,
    )

    appointment.appointment_date = payload.appointment_date
    appointment.slot_time = payload.slot_time
    appointment.reason = payload.reason
    appointment.reschedule_count += 1
    appointment.updated_at = datetime.now()

    add_history(
        db,
        appointment,
        "Booked",
        "Booked",
        current_user.id,
    )

    try:
        db.commit()
        db.refresh(appointment)
    except IntegrityError as error:
        db.rollback()
        print("RESCHEDULE INTEGRITY ERROR:", repr(error.orig))
        raise HTTPException(
            status_code=409,
            detail=f"Database constraint error: {error.orig}",
        )
    except SQLAlchemyError as error:
        db.rollback()
        print("RESCHEDULE DATABASE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Database error while rescheduling the appointment.",
        )

    # Rescheduling email
    patient = appointment.patient
    send_appointment_email(
        recipient=getattr(patient, "email", None),
        subject="Appointment Rescheduled",
        body=(
            "Dear Patient,\n\n"
            "Your hospital appointment has been rescheduled successfully.\n\n"
            f"Appointment Number: {appointment.appointment_number}\n"
            f"New Date: {appointment.appointment_date}\n"
            f"New Time: {appointment.slot_time}\n"
            f"Token Number: {appointment.token_number}\n\n"
            "Thank you."
        ),
    )

    try:
        await manager.broadcast(
            appointment.doctor_id,
            {
                "event": "appointment_rescheduled",
                "appointment_id": appointment.id,
                "appointment_date": str(appointment.appointment_date),
                "slot_time": str(appointment.slot_time),
            },
        )
    except Exception as websocket_error:
        print("WebSocket notification error:", repr(websocket_error))

    return appointment