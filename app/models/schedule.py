from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "day_of_week",
            "start_time",
            name="uq_doctor_schedule_start",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_end: Mapped[time | None] = mapped_column(Time, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    doctor = relationship("Doctor", back_populates="schedules")