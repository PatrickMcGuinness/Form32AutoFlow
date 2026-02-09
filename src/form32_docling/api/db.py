"""Database schema for Form32 GUI persistence."""

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class Patient(Base):
    """Patient record and assessment status."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_name: Mapped[str] = mapped_column(String, index=True)
    ssn: Mapped[str | None] = mapped_column(String)
    exam_date: Mapped[str | None] = mapped_column(String)
    exam_location: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, ready, generated

    # Store full PatientInfo as JSON for easy retrieval/update
    patient_info_json: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    injury_evaluations: Mapped[list["InjuryEvaluation"]] = relationship("InjuryEvaluation", back_populates="patient", cascade="all, delete-orphan")


class InjuryEvaluation(Base):
    """Evaluation of an identified injury or condition."""

    __tablename__ = "injury_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id"))
    condition_text: Mapped[str | None] = mapped_column(String)
    is_substantial_factor: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Store diagnosis codes as a comma-separated string or JSON
    diagnosis_codes_json: Mapped[str] = mapped_column(String, default="[\"\", \"\", \"\", \"\"]")

    patient: Mapped["Patient"] = relationship("Patient", back_populates="injury_evaluations")


def get_db_url() -> str:
    """Get the SQLite database URL."""
    db_path = Path.home() / ".form32_gui.db"
    return f"sqlite:///{db_path}"


engine = create_engine(get_db_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize the database."""
    Base.metadata.create_all(bind=engine)
