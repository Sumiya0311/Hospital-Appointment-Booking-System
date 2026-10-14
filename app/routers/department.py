from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(Department).filter(
        Department.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department already exists",
        )

    department = Department(
        name=data.name,
        description=data.description,
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


@router.get("/", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.id).all()


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    data: DepartmentCreate,
    db: Session = Depends(get_db),
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    duplicate = db.query(Department).filter(
        Department.name == data.name,
        Department.id != department_id,
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department name already exists",
        )

    department.name = data.name
    department.description = data.description

    db.commit()
    db.refresh(department)

    return department