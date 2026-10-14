from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    ForeignKey,
    Boolean,
    Numeric,
    CheckConstraint,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "reschedule_count >= 0",
            name="ck_appointments_reschedule_count",
        ),
        Index(
            "ix_appointments_appointment_number",
            "appointment_number",
            unique=True,
        ),
    )

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Appointment details
    appointment_number = Column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    patient_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True,
    )

    appointment_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    slot_time = Column(
        Time,
        nullable=False,
    )

    token_number = Column(
        Integer,
        nullable=False,
    )

    reason = Column(
        String(1000),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="Booked",
        server_default="Booked",
        index=True,
    )

    consultation_fee = Column(
        Numeric(10, 2),
        nullable=False,
    )

    reschedule_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    reminder_sent = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    patient = relationship(
        "User",
        foreign_keys=[patient_id],
    )

    doctor = relationship(
        "Doctor",
        back_populates="appointments",
        foreign_keys=[doctor_id],
    )

    consultation = relationship(
        "Consultation",
        back_populates="appointment",
        uselist=False,
    )

    history = relationship(
        "AppointmentHistory",
        back_populates="appointment",
    )

    uploaded_files = relationship(
        "UploadedFile",
        back_populates="appointment",
    )