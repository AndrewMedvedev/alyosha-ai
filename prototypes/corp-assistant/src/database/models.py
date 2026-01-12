from datetime import datetime

from sqlalchemy import ARRAY, BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


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

    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str]
    recognition_results: Mapped[list[str]] = mapped_column(ARRAY(String))
