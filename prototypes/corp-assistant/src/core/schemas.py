from typing import Literal

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt

from ..utils import current_datetime

DocumentExt = Literal[".pdf", ".docx", ".md"]


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    username: str | None = None
    fist_name: str | None = None
    last_name: str | None = None
    role: UserRole
    created_at: datetime = Field(default_factory=current_datetime)


class File(BaseModel):
    path: str
    size: PositiveInt
    mime_type: str
    extension: str
    data: bytes


class AudioSegment(BaseModel):
    index: NonNegativeInt
    segments_count: PositiveInt
    data: bytes
    size: PositiveInt
    audio_format: str
    duration_ms: PositiveInt

    @property
    def is_first(self) -> bool:
        return self.index == 0

    @property
    def is_last(self) -> bool:
        return self.index == self.segments_count


class MinutesTask(BaseModel):
    """Задача на составление протокола совещания"""

    audio_paths: list[str]
    user_id: PositiveInt
    max_speakers: PositiveInt
    document_ext: DocumentExt = ".docx"
