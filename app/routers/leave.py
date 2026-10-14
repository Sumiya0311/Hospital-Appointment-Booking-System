from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.doctor import Doctor
from app.models.leave import DoctorLeave
from app.schemas.leave import LeaveCreate, LeaveResponse

router = APIRouter(prefix="/leaves", tags=["Doctor Leaves"])


@router.post("/", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
def create_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    if data.leave_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave date cannot be in the past",
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active doctor not found",
        )

    existing = db.query(DoctorLeave).filter(
        DoctorLeave.doctor_id == data.doctor_id,
        DoctorLeave.leave_date == data.leave_date,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave already exists for this date",
        )

    leave = DoctorLeave(
        doctor_id=data.doctor_id,
        leave_date=data.leave_date,
        reason=data.reason,
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    return leave


@router.get("/doctor/{doctor_id}", response_model=list[LeaveResponse])
def get_doctor_leaves(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return db.query(DoctorLeave).filter(
        DoctorLeave.doctor_id == doctor_id
    ).order_by(DoctorLeave.leave_date).all()