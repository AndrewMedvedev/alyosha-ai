from uuid import UUID

from pydantic import BaseModel, PositiveInt

from .schemas import AudioSegment, OutputDocumentExt


class AudioRecognize(BaseModel):
    task_id: UUID
    user_id: PositiveInt
    audio_segment: AudioSegment


class MinutesOfMeetingDrawUp(BaseModel):
    task_id: UUID
    user_id: PositiveInt
    output_document_ext: OutputDocumentExt
