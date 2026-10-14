from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.doctor import Doctor
from app.models.schedule import DoctorSchedule
from app.schemas.schedule import ScheduleCreate, ScheduleResponse

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("/", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id,
        Doctor.is_active == True,
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Active doctor not found")

    existing = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == data.doctor_id,
        DoctorSchedule.day_of_week == data.day_of_week,
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="A schedule already exists for this doctor and day",
        )

    schedule = DoctorSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


@router.get("/doctor/{doctor_id}", response_model=list[ScheduleResponse])
def get_doctor_schedules(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id
    ).order_by(DoctorSchedule.day_of_week).all()