from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AppointmentHistory(Base):
    __tablename__ = "appointment_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), nullable=False
    )

    old_status: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )

    new_status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    changed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    appointment = relationship(
        "Appointment", back_populates="history"
    )

    user = relationship("User")