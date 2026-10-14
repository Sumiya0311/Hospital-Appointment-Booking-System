from pydantic import BaseModel, ConfigDict, Field


class DoctorCreate(BaseModel):
    user_id: int = Field(gt=0)
    department_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=100)
    specialization: str = Field(min_length=2, max_length=100)
    qualification: str = Field(min_length=2, max_length=100)
    experience_years: int = Field(ge=0, le=60)
    consultation_fee: float = Field(gt=0)
    slot_duration_minutes: int = Field(ge=5, le=120)


class DoctorResponse(BaseModel):
    id: int
    user_id: int
    department_id: int
    name: str
    specialization: str
    qualification: str
    experience_years: int
    consultation_fee: float
    slot_duration_minutes: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)