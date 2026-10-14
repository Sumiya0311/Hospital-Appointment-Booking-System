from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.doctor import Doctor
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationResponse,
)

router = APIRouter(
    prefix="/consultations",
    tags=["Consultations"],
)


@router.post(
    "/",
    response_model=ConsultationResponse,
    status_code=201,
)
def create_consultation(
    data: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Doctor":
        raise HTTPException(
            status_code=403,
            detail="Only doctors can create consultation records",
        )

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == data.appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == appointment.doctor_id)
        .first()
    )

    if not doctor or doctor.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only manage consultations for your own patients",
        )

    if appointment.status != "Booked":
        raise HTTPException(
            status_code=400,
            detail="Consultations require a booked appointment",
        )

    existing = (
        db.query(Consultation)
        .filter(Consultation.appointment_id == appointment.id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="A consultation record already exists for this appointment",
        )

    consultation = Consultation(
        appointment_id=appointment.id,
        symptoms=data.symptoms,
        diagnosis=data.diagnosis,
        prescription=data.prescription,
        advice=data.advice,
        follow_up_date=data.follow_up_date,
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    return consultation


@router.get(
    "/appointment/{appointment_id}",
    response_model=ConsultationResponse,
)
def get_consultation(
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
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )

    if current_user.role == "Patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "Doctor":
        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == appointment.doctor_id)
            .first()
        )
        if not doctor or doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    consultation = (
        db.query(Consultation)
        .filter(Consultation.appointment_id == appointment_id)
        .first()
    )

    if not consultation:
        raise HTTPException(
            status_code=404,
            detail="Consultation record not found",
        )

    return consultation