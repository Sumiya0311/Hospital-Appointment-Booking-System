from datetime import date
from pydantic import BaseModel


class DailyAppointmentReport(BaseModel):
    report_date: date
    total_appointments: int
    booked_appointments: int
    cancelled_appointments: int
    completed_appointments: int


class DoctorAppointmentReport(BaseModel):
    doctor_id: int
    doctor_name: str
    total_appointments: int
    booked_appointments: int
    cancelled_appointments: int
    completed_appointments: int