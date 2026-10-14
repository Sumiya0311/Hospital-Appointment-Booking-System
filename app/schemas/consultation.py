from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class ConsultationCreate(BaseModel):
    appointment_id: int = Field(gt=0)
    symptoms: str = Field(min_length=2, max_length=1000)
    diagnosis: str = Field(min_length=2, max_length=1000)
    prescription: str = Field(min_length=2, max_length=2000)
    advice: str | None = None
    follow_up_date: date | None = None


class ConsultationResponse(BaseModel):
    id: int
    appointment_id: int
    symptoms: str
    diagnosis: str
    prescription: str
    advice: str | None = None
    follow_up_date: date | None = None
    model_config = ConfigDict(from_attributes=True)