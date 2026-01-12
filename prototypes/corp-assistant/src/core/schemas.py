from typing import Literal, Self

from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import magic
from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt

from ..settings import TIMEZONE
from ..utils import current_datetime
from .enums import TaskStatus, UserRole

OutputDocumentExt = Literal["pdf", "docx"]


class User(BaseModel):
    user_id: PositiveInt
    username: str | None = None
    role: UserRole
    created_at: datetime = Field(default_factory=current_datetime)


class File(BaseModel):
    path: str
    size: PositiveInt
    mime_type: str
    data: bytes
    uploaded_at: datetime

    @classmethod
    def from_raw(cls, path: str, data: bytes) -> Self:
        mime = magic.Magic(mime=True)
        file_stat = Path(path).stat()
        return cls(
            path=path,
            size=len(data),
            mime_type=mime.from_buffer(data),
            data=data,
            uploaded_at=datetime.fromtimestamp(file_stat.st_ctime, tz=TIMEZONE),
        )


class Attachment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    uploaded_by: PositiveInt
    original_filename: str
    filepath: str
    mime_type: str
    size: PositiveInt
    uploaded_at: datetime = Field(default_factory=current_datetime)


class AudioSegment(BaseModel):
    serial_number: NonNegativeInt
    total_count: NonNegativeInt
    data: bytes
    size: PositiveInt
    format: str
    duration_ms: PositiveInt

    @property
    def is_first(self) -> bool:
        return self.serial_number == 0

    @property
    def is_last(self) -> bool:
        return self.serial_number == self.total_count - 1


class AudioRecognitionTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=current_datetime)
    updated_at: datetime = Field(default_factory=current_datetime)
    finished_at: datetime | None = None
    status: TaskStatus
    output_document_ext: OutputDocumentExt = "docx"
    recognition_results: list[str] = Field(default_factory=list)

    def change_status(self, status: TaskStatus) -> None:
        self.status = status
