from typing import Literal

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt

from ..utils import current_datetime


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


class AudioSegment(BaseModel):
    """Часть аудио записи"""

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

    audio_path: str
    audio_format: str
    user_id: PositiveInt
    max_speakers: PositiveInt
    output_format: Literal["pdf", "docx", "md"] = "docx"
