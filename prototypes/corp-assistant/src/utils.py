import io
import json
from datetime import datetime

from bs4 import BeautifulSoup, Comment
from bs4.element import NavigableString
from markdown_pdf import MarkdownPdf, Section
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


def md_to_pdf(md_content: str) -> bytes:
    """Формирует PDF файл по Markdown контенту"""

    pdf = MarkdownPdf()
    pdf.add_section(Section(md_content))
    buffer = io.BytesIO()
    pdf.save_bytes(buffer)
    return buffer.getvalue()


def transform_html(html_content: str, max_length: int = 4096) -> str:  # noqa: C901
    """Конвертирует HTML в Telegram совместимую разметку"""

    if not html_content or not html_content.strip():
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    def process_element(element):  # noqa: C901, PLR0911
        """Рекурсивная обработка каждого элемента"""

        if isinstance(element, NavigableString):
            return str(element)
        if isinstance(element, Comment):
            return ""
        tag_name = element.name.lower()
        children_text = "".join(process_element(child) for child in element.children)
        if tag_name in {"b", "strong"}:
            return f"**{children_text}**"
        if tag_name in {"i", "em"}:
            return f"*{children_text}*"
        if tag_name in {"u", "ins"}:
            return f"__{children_text}__"
        if tag_name in {"s", "strike", "del"}:
            return f"~{children_text}~"
        if tag_name == "code":
            return f"`{children_text}`"  # Inline код
        if tag_name == "pre":
            return f"\n```\n{children_text}\n```\n"  # Блок кода
        if tag_name == "a":
            href = element.get("href", "")
            if href and children_text:
                return f"[{children_text}]({href})"
            return children_text
        if tag_name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag_name[1])
            prefix = "\n" + "🔸" * min(level, 3) + " "  # Маркеры для наглядности
            return f"{prefix}**{children_text.upper()}**\n\n"
        if tag_name in {"p", "br"}:
            return f"{children_text}\n"
        if tag_name in {"ul", "ol"}:
            return f"\n{children_text}\n"
        if tag_name == "li":
            parent = element.find_parent(["ul", "ol"])
            if parent and parent.name == "ol":
                index = list(parent.find_all("li", recursive=False)).index(element) + 1
                prefix = f"{index}. "
            else:
                prefix = "• "
            return f"{prefix}{children_text}\n"
        if tag_name == "hr":
            return "\n" + "─" * 20 + "\n"
        if tag_name == "blockquote":
            lines = children_text.strip().split("\n")
            quoted = "\n".join(f"▎ {line}" for line in lines if line.strip())
            return f"\n{quoted}\n"
        if tag_name in {"html", "body", "head", "title", "meta"}:
            return ""
        return children_text

    result = process_element(soup.html or soup)
    lines = [line.strip() for line in result.split("\n")]
    result = "\n".join(line for line in lines if line)
    if len(result) > max_length:
        result = result[: max_length - 3] + "..."
    return result
