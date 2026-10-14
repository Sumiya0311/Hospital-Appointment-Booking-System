from datetime import time

from pydantic import BaseModel, Field, model_validator


class ScheduleCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    break_start: time | None = None
    break_end: time | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")

        if (self.break_start is None) != (self.break_end is None):
            raise ValueError("Provide both break start and break end")

        if self.break_start is not None:
            if not (
                self.start_time < self.break_start
                < self.break_end < self.end_time
            ):
                raise ValueError("Break must be within working hours")

        return self


class ScheduleResponse(BaseModel):
    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    break_start: time | None = None
    break_end: time | None = None

    model_config = {"from_attributes": True}