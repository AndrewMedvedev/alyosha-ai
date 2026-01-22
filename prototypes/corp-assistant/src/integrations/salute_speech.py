from typing import Any, Literal, Self

import asyncio
import json
import logging
import operator
from collections import UserList
from uuid import UUID

import aiohttp
from pydantic import BaseModel

from . import sber_devices

logger = logging.getLogger(__name__)

# Базовый URL сервиса Salute Speech
BASE_URL = "https://smartspeech.sber.ru/rest/v1/"
# Модель для распознавания речи
MODEL = "general"
# Язык для распознавания речи
Language = Literal["ru-RU", "en-US", "kk-KZ", "ky-KG", "uz-UZ"]
# Допустимые кодировки аудио
AudioEncoding = Literal["PCM_S16LE", "OPUS", "MP3", "FLAC", "ALAW", "MULAW", "G729"]
# Конфигурации для допустимых аудио кодировок
AUDIO_ENCODING_CONFIG = {
    "PCM_S16LE": {
        "max_channels": 8,
        "samplerate_range": (8000, 96000),
        "requires_samplerate": False,  # При наличии WAV заголовка,
        "content_type": "audio/x-pcm;bit=16;rate={samplerate}"
    },
    "OPUS": {
        "max_channels": 1,
        "samplerate_range": None,  # Определяется автоматически
        "requires_samplerate": False,
        "content_type": "audio/ogg;codecs=opus"
    },
    "MP3": {
        "max_channels": 2,
        "samplerate_range": None,
        "requires_samplerate": False,
        "content_type": "audio/mpeg"
    },
    "FLAC": {
        "max_channels": 8,
        "samplerate_range": None,
        "requires_samplerate": False,
        "content_type": "audio/flac"
    },
    "ALAW": {
        "max_channels": 1,
        "samplerate_range": (8000, 8000),  # Фиксированная 8 кГц
        "requires_samplerate": True,  # Если нет заголовка WAV
        "content_type": "audio/pcma;rate={samplerate}"
    },
    "MULAW": {
        "max_channels": 1,
        "samplerate_range": (8000, 8000),
        "requires_samplerate": True,
        "content_type": "audio/pcmu;rate={samplerate}"
    },
    "G729": {
        "max_channels": 1,
        "samplerate_range": (8000, 8000),
        "requires_samplerate": False,
        "content_type": "audio/g729"
    }
}


class SaluteSpeechError(Exception):
    pass


class UploadingFailedError(SaluteSpeechError):
    """Ошибка загрузки файла"""


class TaskFailedError(SaluteSpeechError):
    """Ошибка при выполнении задачи"""


class DownloadingFailedError(SaluteSpeechError):
    """Ошибка скачивания файла"""


async def _upload_file(
        data: bytes,
        audio_encoding: str,
        channels: int = 1,
        samplerate: int | None = None,
        use_ssl: bool = False,
) -> UUID:
    if samplerate is None:
        samplerate = 16_000
    config = AUDIO_ENCODING_CONFIG.get(audio_encoding)
    if config is None:
        raise ValueError(
            f"Unsupported audio encoding format! Input format {audio_encoding},"
            f"supported formats {', '.join(list(AUDIO_ENCODING_CONFIG.keys()))}"
        )
    if channels > config["max_channels"]:
        raise ValueError(
            f"Format {audio_encoding} supports max {config['max_channels']} "
            f"channels, but got {channels}"
        )
    if config["samplerate_range"] is not None:
        min_samplerate, max_samplerate = config["samplerate_range"]
        if not (min_samplerate < samplerate < max_samplerate):
            raise ValueError(
                f"Format {audio_encoding} requires sample rate between "
                f"{min_samplerate} and {max_samplerate} Hz, but got {samplerate} Hz"
            )
    access_token = await sber_devices.authenticate()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": config["content_type"].format(samplerate=samplerate),
    }
    url = f"{BASE_URL}data:upload"
    try:
        logger.info(
            "Start uploading file %s mb to Salute Speech with encoding %s",
            round(len(data) / 1_000_000, 2), audio_encoding
        )
        async with aiohttp.ClientSession() as session, session.post(
                url=url, headers=headers, data=data, ssl=use_ssl
        ) as response:
            response.raise_for_status()
            data = await response.json()
        logger.info("File successfully uploaded")
        return UUID(data["result"]["request_file_id"])
    except aiohttp.ClientResponseError as e:
        error_message = f"Uploading failed with {response.status} status, error: {e}"
        logger.exception(error_message)
        raise UploadingFailedError(error_message) from e
    except aiohttp.ClientError as e:
        error_message = f"An unexpected error occurred while uploading file: {e}"
        logger.exception(error_message)
        raise UploadingFailedError(error_message) from e


async def _create_task(
        request_file_id: UUID,
        audio_encoding: AudioEncoding,
        diarization: bool = True,
        max_speakers: int = 1,
        language: Language = "ru-RU",
        channels: int = 1,
        samplerate: int = 16_000,
        words: list[str] | None = None,
        enable_letters: bool = False,
        eou_timeout: int = 1,
        profanity_check: bool = False,
        use_ssl: bool = False,
) -> dict[str, Any]:
    """Создание задачи на распознавание.

    :param request_file_id: Идентификатор загруженного файла.
    :param audio_encoding: Аудио-кодек.
    :param diarization: Разделение по спикерам.
    :param max_speakers: Максимальное число спикеров.
    :param language: Язык для распознавания речи.
    :param channels: Количество каналов аудио.
    :param samplerate: Частота дискретизации аудио.
    :param words: Список слов или фраз, распознавание которых мы хотим усилить.
    :param enable_letters: Модель коротких фраз, улучшающая распознавание коротких слов.
    :param eou_timeout: Настройка распознавания конца фразы (End of Utterance — eou).
    :returns: Созданная задача со статусом 'NEW'.
    """

    access_token = await sber_devices.authenticate()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Request-ID": f"{request_file_id}",
    }
    payload = {
        "options": {
            "model": MODEL,
            "audio_encoding": audio_encoding,
            "sample_rate": samplerate,
            "language": language,
            "enable_profanity_filter": profanity_check,
            "channels_count": channels,
            "speaker_separation_options": {
                "enable": diarization,
                "enable_only_main_speaker": False,
                "count": min(max_speakers, 10),
                # Ограничение на максимальное количество спикеров
            },
        },
        "request_file_id": f"{request_file_id}",
    }
    if words:
        payload["hints"] = {
            "words": words,
            "enable_letters": enable_letters,
            "eou_timeout": eou_timeout,
        }
    url = f"{BASE_URL}speech:async_recognize"
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                url=url,
                headers=headers,
                data=json.dumps(payload),
                ssl=use_ssl,
            ) as response,
        ):
            response.raise_for_status()
            data = await response.json()
        return data["result"]
    except aiohttp.ClientResponseError as e:
        error_message = f"Task creation failed with status {e.status} error: {e.message}"
        logger.exception(error_message)
        raise TaskFailedError(error_message) from e
    except aiohttp.ClientError as e:
        error_message = f"An error occurred while task creation, error {e}"
        logger.exception(error_message)
        raise TaskFailedError(error_message) from e


async def _get_task_status(task_id: str, use_ssl: bool = False) -> dict[str, Any]:
    access_token = await sber_devices.authenticate()
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"id": task_id}
    payload = {}
    url = f"{BASE_URL}task:get"
    try:
        async with aiohttp.ClientSession() as session, session.get(
                url=url,
                headers=headers,
                params=params,
                data=json.dumps(payload),
                ssl=use_ssl,
        ) as response:
            response.raise_for_status()
            data = await response.json()
        return data["result"]
    except aiohttp.ClientResponseError as e:
        error_message = f"Task receiving failed with status {e.status} error: {e.message}"
        logger.exception(error_message)
        raise TaskFailedError(error_message) from e
    except aiohttp.ClientError as e:
        error_message = f"An error occurred while task receiving, error {e}"
        logger.exception(error_message)
        raise TaskFailedError(error_message) from e


class RecognizedResult(BaseModel):
    text: str
    speaker: int | None = None
    emotion: str | None = None

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        return cls(
            text=response["results"][0]["normalized_text"],
            speaker=response["speaker_info"]["speaker_id"],
            emotion=cls._parse_emotion(response["emotions_result"]),
        )

    @staticmethod
    def _parse_emotion(emotions_result: dict[str, float]) -> str:
        return max(emotions_result.items(), key=operator.itemgetter(1))[0]


class RecognizedResults(UserList[RecognizedResult]):
    def to_markdown(self) -> str:
        if not self.data:
            return "No speech recognized"
        lines: list[str] = []
        for i, recognized_speech in enumerate(self.data):
            parts = [f"{i}. {recognized_speech.text}"]
            if recognized_speech.speaker is not None:
                parts.append(f"({recognized_speech.speaker})")
            if recognized_speech.emotion is not None:
                parts.append(f"[{recognized_speech.emotion}]")
            lines.append(" ".join(parts))
        return "\n".join(lines)


async def _download_file(response_file_id: str, use_ssl: bool = False) -> RecognizedResults:
    access_token = await sber_devices.authenticate()
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/octet-stream"}
    params = {"response_file_id": response_file_id}
    payload = {}
    url = f"{BASE_URL}data:download"
    try:
        async with aiohttp.ClientSession() as session, session.get(
                url=url,
                headers=headers,
                params=params,
                data=payload,
                ssl=use_ssl,
        ) as response:
            response.raise_for_status()
            data = await response.text()
        results = json.loads(data)
        return RecognizedResults([
            RecognizedResult.from_response(result) for result in results
        ])
    except aiohttp.ClientResponseError as e:
        error_message = f"Downloading failed with status {e.status} error: {e.message}"
        logger.exception(error_message)
        raise DownloadingFailedError(error_message) from e
    except aiohttp.ClientError as e:
        error_message = f"An error occurred while downloading, error {e}"
        logger.exception(error_message)
        raise DownloadingFailedError(error_message) from e


async def recognize_async(
        audio_data: bytes,
        audio_encoding: AudioEncoding,
        channels: int = 1,
        max_speakers: int = 10,
        interval: int = 1,
        use_ssl: bool = False,
) -> str:
    """Выполняет асинхронную транскрипцию + диаризацию аудио записи.
    Возвращает результат в формате Markdown.
    """

    request_file_id = await _upload_file(
        audio_data, audio_encoding=audio_encoding, use_ssl=use_ssl
    )
    task = await _create_task(
        request_file_id,
        audio_encoding=audio_encoding,
        channels=channels,
        max_speakers=max_speakers,
        use_ssl=use_ssl,
    )
    while task["status"] != "DONE":
        await asyncio.sleep(interval)
        task = await _get_task_status(task["id"], use_ssl=use_ssl)
    results = await _download_file(task["response_file_id"])
    return results.to_markdown()
