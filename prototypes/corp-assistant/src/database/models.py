from datetime import datetime

from sqlalchemy import ARRAY, BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    fist_name: Mapped[str | None] = mapped_column(nullable=True)
    last_name: Mapped[str | None] = mapped_column(nullable=True)
    role: Mapped[str]


class Attachment(Base):
    __tablename__ = "attachments"

    uploaded_by: Mapped[int] = mapped_column(BigInteger)
    original_filename: Mapped[str]
    filepath: Mapped[str] = mapped_column(unique=True)
    mime_type: Mapped[str]
    size: Mapped[int]
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AudioRecognitionTask(Base):
    __tablename__ = "audio_recognition_tasks"

    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str]
    max_speakers_count: Mapped[int]
    output_document_ext: Mapped[str]
    recognition_results: Mapped[list[str]] = mapped_column(ARRAY(String))
