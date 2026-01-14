import io
import logging
from collections.abc import Iterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydub import AudioSegment
from pydub.utils import make_chunks

from .. import utils
from ..broker import broker
from ..core import enums, events, schemas
from ..database import crud, models
from ..settings import PROMPTS_DIR, settings
from . import media

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "ogg", "flac"}


def _split_audio_on_segments(
        audio_data: bytes, audio_format: str, segment_duration_ms: int = 60 * 20 * 1000
) -> Iterator[schemas.AudioSegment]:
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
            serial_number=i,
            total_count=chunks_count,
            data=chunk_data,
            size=len(chunk_data),
            format="wav",
            duration_ms=segment_duration_ms
        )


async def download_telegram_audio_files(
        user_id: int, tg_file_ids: list[str]
) -> list[schemas.Attachment]:
    from ..bot import bot  # noqa: PLC0415

    attachments: list[schemas.Attachment] = []
    for tg_file_id in tg_file_ids:
        tg_file = await bot.get_file(tg_file_id)
        tg_file_ext = tg_file.file_path.split(".")[-1]
        if tg_file_ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(f"Not supported audio format: {tg_file_ext}!")
        tg_file_buffer = await bot.download_file(
            file_path=tg_file.file_path, destination=io.BytesIO()
        )
        attachment = await media.upload(
            user_id=user_id,
            filename=tg_file.file_path,
            data=tg_file_buffer.getbuffer().tobytes()
        )
        attachments.append(attachment)
    return attachments


async def create_task(
        user_id: int,
        tg_file_ids: list[str],
        participants_count: int = 10,
        output_document_ext: schemas.OutputDocumentExt = "pdf",
) -> None:
    attachments = await download_telegram_audio_files(user_id, tg_file_ids)
    task = schemas.AudioRecognitionTask(
        status=enums.TaskStatus.PENDING,
        max_speakers_count=participants_count,
        output_document_ext=output_document_ext
    )
    await crud.create(task, model_class=models.AudioRecognitionTask)
    for attachment in attachments:
        file = await media.download(attachment.id)
        for audio_segment in _split_audio_on_segments(
            audio_data=file.data, audio_format=file.path.split(".")[-1]
        ):
            event = events.AudioRecognize(
                task_id=task.id, user_id=user_id, audio_segment=audio_segment
            )
            await broker.publish(event, channel="audio:recognize")


async def generate(audio_transcription: str) -> str:
    model = ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3,
    )
    prompt = ChatPromptTemplate.from_template(
        (PROMPTS_DIR / "minutes_of_meeting_prompt.md").read_text(encoding="utf-8")
    )
    chain = prompt | model | StrOutputParser()
    return await chain.ainvoke({"audio_transcription": audio_transcription})


def create_document(md_text: str, output_document_ext: schemas.OutputDocumentExt) -> bytes:
    match output_document_ext:
        case "docx":
            return utils.create_docx_file_from_markdown(md_text)
        case "pdf":
            return utils.create_pdf_file_from_markdown(md_text)
        case _:
            return utils.create_md_file_from_markdown(md_text)
