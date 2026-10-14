import os
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.file import UploadedFile
from app.schemas.file import UploadedFileResponse

router = APIRouter(prefix="/files", tags=["Medical Files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post(
    "/appointment/{appointment_id}",
    response_model=UploadedFileResponse,
    status_code=201,
)
async def upload_medical_file(
    appointment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "Patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "Doctor":
        if not appointment.doctor or appointment.doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG, JPG, and JPEG files are allowed",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 5 MB",
        )

    stored_name = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / stored_name

    try:
        with open(file_path, "wb") as output:
            output.write(content)

        uploaded = UploadedFile(
            appointment_id=appointment_id,
            uploaded_by=current_user.id,
            file_type=extension.lstrip("."),
            original_name=os.path.basename(file.filename or "upload"),
            stored_name=stored_name,
            size_kb=round(len(content) / 1024, 2),
        )

        db.add(uploaded)
        db.commit()
        db.refresh(uploaded)
        return uploaded

    except Exception:
        db.rollback()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded file",
        )

    finally:
        await file.close()


@router.get(
    "/appointment/{appointment_id}",
    response_model=list[UploadedFileResponse],
)
def list_medical_files(
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
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "Patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "Doctor":
        if not appointment.doctor or appointment.doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return (
        db.query(UploadedFile)
        .filter(UploadedFile.appointment_id == appointment_id)
        .order_by(UploadedFile.id.desc())
        .all()
    )