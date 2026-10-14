from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.schemas.report import (
    DailyAppointmentReport,
    DoctorAppointmentReport,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


def require_admin(current_user):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )


@router.get("/daily", response_model=DailyAppointmentReport)
def daily_report(
    report_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user)

    rows = (
        db.query(Appointment.status, func.count(Appointment.id))
        .filter(Appointment.appointment_date == report_date)
        .group_by(Appointment.status)
        .all()
    )

    counts = {status: count for status, count in rows}

    return DailyAppointmentReport(
        report_date=report_date,
        total_appointments=sum(counts.values()),
        booked_appointments=counts.get("Booked", 0),
        cancelled_appointments=counts.get("Cancelled", 0),
        completed_appointments=counts.get("Completed", 0),
    )


@router.get("/doctors", response_model=list[DoctorAppointmentReport])
def doctor_reports(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user)

    doctors = db.query(Doctor).all()
    reports = []

    for doctor in doctors:
        rows = (
            db.query(Appointment.status, func.count(Appointment.id))
            .filter(Appointment.doctor_id == doctor.id)
            .group_by(Appointment.status)
            .all()
        )

        counts = {status: count for status, count in rows}

        reports.append(
            DoctorAppointmentReport(
                doctor_id=doctor.id,
                doctor_name=doctor.name,
                total_appointments=sum(counts.values()),
                booked_appointments=counts.get("Booked", 0),
                cancelled_appointments=counts.get("Cancelled", 0),
                completed_appointments=counts.get("Completed", 0),
            )
        )

    return reports