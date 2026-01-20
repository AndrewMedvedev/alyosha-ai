import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..core import schemas
from ..core.schemas import DocumentExt
from ..settings import PROMPTS_DIR, settings

logger = logging.getLogger(__name__)

SUPPORTED_AUDIO_FORMATS = {"wav", "mp3", "m4a", "ogg", "flac"}

minutes_of_meeting_prompt = (
        PROMPTS_DIR / "minutes_of_meeting_prompt.md"
).read_text(encoding="utf-8")


async def create_minutes_task(
        user_id: int,
        file_ids: list[str],
        max_speakers: int = 10,
        document_ext: DocumentExt = ".pdf",
) -> None:
    from ..bot import bot  # noqa: PLC0415
    from ..broker import broker  # noqa: PLC0415

    audio_paths: list[str] = []
    for file_id in file_ids:
        file = await bot.get_file(file_id, request_timeout=300)
        file_format = file.file_path.split(".")[-1]
        if file_format not in SUPPORTED_AUDIO_FORMATS:
            logger.warning("Not supported audio format: %s!", file_format)
            continue
        audio_paths.append(file.file_path)
    task = schemas.MinutesTask(
        audio_paths=audio_paths,
        user_id=user_id,
        max_speakers=max_speakers,
        document_ext=document_ext
    )
    await broker.publish(task, channel="minutes:draw_up")


async def generate_meeting_minutes(transcription: str) -> str:
    """Генерирует протокол совещания по его транскрибации.

    :param transcription: Транскрибация совещания.
    :returns: Составленный протокол в Markdown формате.
    """

    model = ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3,
    )
    prompt = ChatPromptTemplate.from_template(minutes_of_meeting_prompt)
    chain = prompt | model | StrOutputParser()
    return await chain.ainvoke({"transcription": transcription})
