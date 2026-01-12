from aiogram.types import BufferedInputFile
from faststream import FastStream, Logger
from faststream.redis import RedisBroker

from .ai_agents.minutes_of_meeting_compiler import agent
from .bot.bot import bot
from .core import enums, events, schemas
from .database import crud, models
from .integrations import salute_speech
from .services import minutes_of_meetings as minutes_of_meetings_service
from .utils import current_datetime

broker = RedisBroker(...)

app = FastStream(broker)


@broker.subscriber("audio:recognize")
async def handle_audio_recognize_event(event: events.AudioRecognize, logger: Logger) -> None:
    if event.audio_segment.is_first:
        await bot.send_message(
            chat_id=event.user_id, text="Транскрибация вашей аудиозаписи началась..."
        )
    recognition_result = await salute_speech.recognize_async(
        audio_data=event.audio_segment.data,
        audio_encoding="PCM_S16LE",
        max_speakers_count=10,
    )
    current_task = await crud.read(
        event.task_id,
        model_class=models.AudioRecognitionTask,
        schema_class=schemas.AudioRecognitionTask
    )
    current_task.recognition_results.append(recognition_result)
    await crud.refresh(current_task, model_class=models.AudioRecognitionTask)
    if event.audio_segment.is_last:
        logger.info("Recognition task `%s` finished", event.task_id)
        current_task.change_status(enums.TaskStatus.COMPLETED)
        await crud.refresh(current_task, model_class=models.AudioRecognitionTask)
        logger.info("Broadcast task `%s` to minutes of meeting compiler", event.task_id)
        await broker.publish(
            events.MinutesOfMeetingDrawUp(
                task_id=event.task_id,
                user_id=event.user_id,
                output_document_ext=current_task.output_document_ext
            ),
            channel="minutes_of_meeting:draw_up"
        )
        await bot.send_message(
            chat_id=event.user_id,
            text="""Транскрибация вашей аудиозаписи завершена.
            Начинаю составлять протокол ...
            """
        )


@broker.subscriber("minutes_of_meeting:draw_up")
async def draw_up_minutes_of_meeting(
        event: events.MinutesOfMeetingDrawUp, logger: Logger
) -> None:
    task = await crud.read(
        event.task_id,
        model_class=models.AudioRecognitionTask,
        schema_class=schemas.AudioRecognitionTask
    )
    audio_transcription = "\n".join(task.recognition_results)
    logger.info("Start compile minutes of meeting for user `%s`", event.user_id)
    minutes_of_meeting = await agent.ainvoke({"audio_transcription": audio_transcription})
    document_data = minutes_of_meetings_service.create_document(
        md_text=minutes_of_meeting, output_document_ext=event.output_document_ext
    )
    await bot.send_document(
        chat_id=event.user_id, document=BufferedInputFile(
            document_data,
            filename=f"Протокол_совещания_{current_datetime()}.{event.output_document_ext}"
        )
    )
