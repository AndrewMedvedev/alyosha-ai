from typing import Any, Self

from enum import StrEnum
from uuid import UUID

from pydantic import Field, NonNegativeInt, ValidationError, model_validator

from modules.shared_kernel.domain import ValueObject


class MessageRole(StrEnum):
    """Роль сообщения"""

    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class ContentType(StrEnum):
    """Тип контента текстового сообщения"""

    TEXT = "text"
    MARKDOWN = "markdown"
    CODE = "code"
    ERROR = "error"
    EMPTY = "empty"


class ContentBlock(ValueObject):
    """Блок с контентом внутри сообщения"""

    content_type: ContentType
    text: str | None = None
    attachments: list[UUID] = Field(default_factory=list)


class TokenType(StrEnum):
    """Разновидности токенов (для точной тарификации)"""

    PROMPT = "prompt"
    COMPLETION = "completion"
    REASONING = "reasoning"


class TokenUsage(ValueObject):
    """Использование токенов"""

    token_type: TokenType
    tokens_count: NonNegativeInt
    total_tokens: NonNegativeInt | None = None

    @model_validator(mode="after")
    def validate_total_tokens(self) -> Self:
        if self.total_tokens < self.tokens_count:
            raise ValidationError(
                f"Total tokens ({self.total_tokens}) cannot be less than "
                f"type-specific tokens ({self.tokens_count}) for {self.token_type}"
            )
        return self


class MessageMetadata(ValueObject):
    """Метаданные сообщения.

    Attributes:
        token_usage: Счетчики и метрики потраченных токенов.
        artifacts: Полезная нагрузка, которая не будет передана в ассистента.
    """

    token_usage: TokenUsage
    artifacts: dict[str, Any] = Field(default_factory=dict)
