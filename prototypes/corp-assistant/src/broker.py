from faststream import FastStream, Logger
from faststream.redis import RedisBroker

from .core import enums, events, schemas
from .database import crud, models
from .integrations import salute_speech

broker = RedisBroker(...)

app = FastStream(broker)


@broker.subscriber("audio:recognize")
async def handle_audio_recognize_event(event: events.AudioRecognize, logger: Logger):
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
        current_task.change_status(enums.TaskStatus.COMPLETED)
        await crud.refresh(current_task, model_class=models.AudioRecognitionTask)
        await broker.publish(..., channel="minutes_of_meeting:draw_up")


@broker.subscriber("minutes_of_meeting:draw_up")
async def draw_up_minutes_of_meeting() -> ...: ...
