from typing import Literal, Self

import base64
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import magic
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeInt,
    PositiveInt,
    field_serializer,
    field_validator,
)

from ..settings import TIMEZONE
from ..utils import current_datetime
from .enums import TaskStatus, UserRole

OutputDocumentExt = Literal["pdf", "docx", "md"]


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: PositiveInt
    username: str | None = None
    fist_name: str | None = None
    last_name: str | None = None
    role: UserRole
    created_at: datetime = Field(default_factory=current_datetime)

    @property
    def full_name(self) -> str:
        return f"{self.fist_name} {self.last_name}"


class File(BaseModel):
    path: str
    size: PositiveInt
    mime_type: str
    data: bytes
    uploaded_at: datetime

    @classmethod
    def from_raw(cls, path: str, data: bytes) -> Self:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(data)
        file_stat = Path(path).stat()
        return cls(
            path=path,
            size=len(data),
            mime_type=mime_type,
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
    total_count: PositiveInt
    data: bytes
    size: PositiveInt
    format: str
    duration_ms: PositiveInt

    @field_serializer("data")
    def serialize_data(self, data: bytes) -> str:  # noqa: PLR6301
        return base64.b64encode(data).decode("utf-8")

    @field_validator("data", mode="before")
    def decode_data(cls, data: str | bytes) -> bytes:
        if isinstance(data, str):
            return base64.b64decode(data)
        return data

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
    max_speakers_count: PositiveInt
    output_document_ext: OutputDocumentExt = "docx"
    recognition_results: list[str] = Field(default_factory=list)

    def change_status(self, status: TaskStatus) -> None:
        self.status = status
