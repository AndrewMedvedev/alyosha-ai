from pydantic import BaseModel, FilePath, PositiveInt

from .enums import DocumentCategory, DocumentSource


class Document(BaseModel):
    """Документ загруженный в систему пользователем"""

    path: FilePath
    filename: str
    size: PositiveInt
    category: DocumentCategory
    source: DocumentSource
