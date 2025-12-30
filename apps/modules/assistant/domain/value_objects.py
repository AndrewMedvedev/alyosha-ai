from enum import StrEnum
from uuid import UUID

from pydantic import HttpUrl

from modules.shared_kernel.domain import ValueObject

DEFAULT_TEMPERATURE = 0.7


class IntegrationStatus(StrEnum):
    """Статус подключенной LLM к рабочему пространству"""

    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    TESTING = "testing"


class Provider(StrEnum):
    GIGACHAT = "GigaChat"
    YANDEX_CLOUD = "YandexCloud"
    OPENAI = "OpenAI"


class IntegrationConfig(ValueObject):
    """Конфигурация модели"""

    credentials_id: UUID
    provider: Provider
    model_name: str
    base_url: HttpUrl | None = None
    temperature: float = DEFAULT_TEMPERATURE
