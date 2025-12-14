from enum import StrEnum


class DocumentSource(StrEnum):
    """Источник документа (каким приложением он был сформирован)"""

    MS_WORD = "Microsoft Word"
    EXCEL = "Microsoft Excel"
    POWERPOINT = "Microsoft Powerpoint"
    PDF = "pdf"
    AUDIO = "audio"
    VIDEO = "video"
    UNKNOWN = "unknown"


class DocumentCategory(StrEnum):
    """Категория контента к которой относится документ"""

    TEXT = "text"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    UNKNOWN = "unknown"
