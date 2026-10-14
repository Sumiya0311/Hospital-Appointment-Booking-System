from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.department import Department
from app.schemas.doctor import DoctorCreate, DoctorResponse 

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "Doctor":
        raise HTTPException(
            status_code=400,
            detail="The selected user must have the Doctor role",
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")

    existing_doctor = db.query(Doctor).filter(
        Doctor.user_id == data.user_id
    ).first()

    if existing_doctor:
        raise HTTPException(
            status_code=409,
            detail="Doctor profile already exists for this user",
        )

    department = db.query(Department).filter(
        Department.id == data.department_id
    ).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    doctor = Doctor(
        user_id=data.user_id,
        department_id=data.department_id,
        name=data.name,
        specialization=data.specialization,
        qualification=data.qualification,
        experience_years=data.experience_years,
        consultation_fee=data.consultation_fee,
        slot_duration_minutes=data.slot_duration_minutes,
        is_active=True,
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


@router.get("/", response_model=list[DoctorResponse])
def list_doctors(
    department_id: int | None = None,
    specialization: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Doctor).filter(Doctor.is_active.is_(True))

    if department_id is not None:
        query = query.filter(Doctor.department_id == department_id)

    if specialization:
        query = query.filter(
            Doctor.specialization.ilike(f"%{specialization}%")
        )

    return query.order_by(Doctor.id).all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    data: DoctorCreate,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user or user.role != "Doctor" or not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="An active user with the Doctor role is required",
        )

    duplicate = db.query(Doctor).filter(
        Doctor.user_id == data.user_id,
        Doctor.id != doctor_id,
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Doctor profile already exists for this user",
        )

    department = db.query(Department).filter(
        Department.id == data.department_id
    ).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    for field, value in data.model_dump().items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)

    return doctor


@router.delete("/{doctor_id}")
def deactivate_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.is_active = False
    db.commit()

    return {"message": "Doctor deactivated successfully"}