from pydantic import BaseModel, Field


class QueueMessage(BaseModel):
    message: str
    doctor_id: int = Field(gt=0)


class QueueStatusResponse(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_id: int = Field(gt=0)
    token_number: int = Field(gt=0)
    status: str