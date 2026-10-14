from datetime import date, time, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_date: date
    slot_time: time
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("slot_time")
    @classmethod
    def validate_slot_time(cls, value: time) -> time:
        if value.second != 0 or value.microsecond != 0:
            raise ValueError(
                "Appointment time must not include seconds or microseconds"
            )
        return value


class AppointmentResponse(BaseModel):
    id: int
    appointment_number: str
    patient_id: int
    doctor_id: int
    appointment_date: date
    slot_time: time
    token_number: int
    reason: str | None = None
    status: str
    consultation_fee: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)