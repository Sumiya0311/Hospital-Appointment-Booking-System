from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class LeaveCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    leave_date: date
    reason: str = Field(min_length=3, max_length=255)


class LeaveResponse(BaseModel):
    id: int
    doctor_id: int
    leave_date: date
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True)