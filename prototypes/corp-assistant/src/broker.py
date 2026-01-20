import io
import logging
from collections.abc import Iterator

import magic
from aiogram import Bot
from aiogram.types import BufferedInputFile, Message
from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from pydub import AudioSegment
from pydub.utils import make_chunks

from .core import schemas
from .integrations import salute_speech
from .services.minutes import generate_meeting_minutes
from .settings import settings
from .utils import audio_mime_to_ext, current_datetime, progress_emojis

logger = logging.getLogger(__name__)

broker = RedisBroker(
    settings.redis.url,
    socket_timeout=120.0,
    socket_connect_timeout=15.0,
    socket_keepalive=True,
    retry_on_timeout=True,
    health_check_interval=15
)

app = FastStream(broker)


def split_audio_into_segments(
        audio_data: bytes, audio_format: str, segment_duration_ms: int = 60 * 20 * 1000
) -> Iterator[schemas.AudioSegment]:
    """Разделяет аудио файл на сегменты с заданной продолжительностью.

    :param audio_data: Байты аудио файла.
    :param audio_format: Формат аудио, например: 'wav', 'ogg', 'm4a'.
    :param segment_duration_ms: Продолжительность сегмента в миллисекундах.
    :returns: Объекты аудио сегментов.
    """

    logger.info("Start split audio on segments...")
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format)
    chunks = make_chunks(audio, segment_duration_ms)
    chunks_count = len(chunks)
    logger.info("Created %s segments from audio", chunks_count)
    for i, chunk in enumerate(chunks):
        buffer = io.BytesIO()
        chunk.export(buffer, format="wav", bitrate="192k")
        logger.info("Export %s segment data to WAV format", i)
        chunk_data = buffer.getvalue()
        yield schemas.AudioSegment(
            index=i,
            segments_count=chunks_count,
            data=chunk_data,
            size=len(chunk_data),
            audio_format="wav",
            duration_ms=segment_duration_ms
        )


async def update_progress(
        bot: Bot, chat_id: int, percent: float, prev_message_id: int | None = None
) -> Message:
    """Обновляет сообщение с прогрессом расшифровки аудио записи"""

    text = f"""
    Расшифровываю аудио ...
    {progress_emojis(percent)}
    <b>{percent:.1f}%</b>
    """
    await bot.delete_message(chat_id=chat_id, message_id=prev_message_id)
    return await bot.send_message(chat_id=chat_id, text=text)


@broker.subscriber("minutes:draw_up")
async def process_minutes_task(task: schemas.MinutesTask, logger: Logger) -> None:
    from .bot import bot  # noqa: PLC0415

    bot_message = await bot.send_message(
        chat_id=task.user_id,
        text="Начинаю обработку аудио записи, это может занять от 5 до 15 минут ⏳..."
    )
    transcription_segments: list[str] = []
    for audio_path in task.audio_paths:
        file_buffer = await bot.download_file(audio_path, destination=io.BytesIO())
        audio_data = file_buffer.getbuffer().tobytes()
        mime_type = magic.Magic(mime=True).from_buffer(audio_data)
        for audio_segment in split_audio_into_segments(
                audio_data, audio_format=audio_mime_to_ext(mime_type)
        ):
            bot_message = await update_progress(
                bot=bot,
                chat_id=task.user_id,
                percent=audio_segment.index + 1 / audio_segment.segments_count,
                prev_message_id=bot_message.message_id
            )
            logger.info(
                "Recognizing %s segment of audio file %s", audio_segment.index + 1, audio_path
            )
            transcription = await salute_speech.recognize_async(
                audio_data=audio_segment.data,
                audio_encoding="PCM_S16LE",
                max_speakers=task.max_speakers,
            )
            transcription_segments.append(transcription)
    full_transcription = "\n".join(transcription_segments)
    await bot.delete_message(chat_id=task.user_id, message_id=bot_message.message_id)
    await bot.send_message(
        chat_id=task.user_id,
        text="Всё распознано! 🎤\nФормирую протокол совещания… ✍️\nЭто займёт ещё 30–90 секунд",
    )
    minutes_md = await generate_meeting_minutes(full_transcription)
    md_file = io.BytesIO()
    md_file.write(minutes_md.encode("utf-8"))
    md_file.seek(0)
    await bot.send_document(
        chat_id=task.user_id, document=BufferedInputFile(
            file=md_file.getvalue(),
            filename=f"Прокол_совещания_{current_datetime()}.md"
        ),
        caption="Готово! 🎉"
    )
