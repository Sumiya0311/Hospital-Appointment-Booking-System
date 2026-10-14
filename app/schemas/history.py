from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AppointmentHistoryResponse(BaseModel):
    id: int
    appointment_id: int
    old_status: str | None = None
    new_status: str
    changed_by: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)