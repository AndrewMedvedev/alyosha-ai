import io
import json
from datetime import datetime

from markitdown import MarkItDown

from .settings import AUDIO_MIME_TO_EXT_JSON, TIMEZONE


def current_datetime() -> datetime:
    """Получение текущего времени в выбранном часовом поясе"""

    return datetime.now(TIMEZONE)


def audio_mime_to_ext(mime_type: str) -> str:
    """Получение расширения аудио файла по его Mime-type"""

    mime_to_ext_map = json.loads(AUDIO_MIME_TO_EXT_JSON.read_text(encoding="utf-8"))
    return mime_to_ext_map[mime_type]


def convert_document_to_md(data: bytes, extension: str) -> str:
    """Конвертирует контент документа (.pptx, .pdf, .docx, .xlsx) в Markdown текст.

    :param data: Байты исходного документа.
    :param extension: Расширение документа, например: .pdf, .docx, .xlsx
    :returns: Markdown текст.
    """

    md = MarkItDown()
    result = md.convert_stream(io.BytesIO(data), file_extension=extension)
    return result.text_content


def escape_md2(text: str) -> str:
    """Экранирует специальные символы для Markdown V2"""

    chars_to_escape = r"_[]()~`>#+-=|{}.!"
    for char in chars_to_escape:
        text = text.replace(char, f"\\{char}")
    return text


def progress_emojis(perc: float, width: int = 10) -> str:
    filled = round(width * perc / 100)
    return "🌕" * filled + "🌑" * (width - filled)
