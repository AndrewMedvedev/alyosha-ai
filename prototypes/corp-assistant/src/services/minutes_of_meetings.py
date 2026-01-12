import io
import logging
from collections.abc import Iterator
from uuid import UUID

from pydub import AudioSegment
from pydub.utils import make_chunks

from ..broker import broker
from ..core import enums, events, schemas
from . import media as media_service

logger = logging.getLogger(__name__)


def _split_audio_on_segments(
        audio_data: bytes, audio_format: str, segment_duration_ms: int = 60 * 20 * 100
) -> Iterator[schemas.AudioSegment]:
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format)
    chunks = make_chunks(audio, segment_duration_ms)
    chunks_count = len(chunks)
    for i, chunk in enumerate(chunks):
        buffer = io.BytesIO()
        chunk.export(buffer, format="wav", bitrate="192k")
        chunk_data = buffer.getvalue()
        yield schemas.AudioSegment(
            serial_number=i,
            total_count=chunks_count,
            data=chunk_data,
            size=len(chunk_data),
            format="wav",
            duration_ms=segment_duration_ms
        )


async def create_task(user_id: int, file_ids: list[UUID]) -> ...:
    task = schemas.AudioRecognitionTask(status=enums.TaskStatus.PENDING)
    for file_id in file_ids:
        file = await media_service.download(file_id)
        for audio_segment in _split_audio_on_segments(
            audio_data=file.data, audio_format=file.path.split(".")[-1]
        ):
            event = events.AudioRecognize(
                task_id=task.id, user_id=user_id, audio_segment=audio_segment
            )
            await broker.publish(event, channel="audio:recognize")
