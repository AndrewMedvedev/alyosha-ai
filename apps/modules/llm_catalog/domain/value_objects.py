from decimal import Decimal
from enum import StrEnum

from pydantic import NonNegativeInt, PositiveInt

from modules.shared_kernel.domain import ValueObject


class LLMCategory(StrEnum):
    OPEN_SOURCE = "open-source"
    COMMERCIAL = "commercial"


class DeploymentType(StrEnum):
    """Тип развёртывания модели"""

    LOCAL = "local"
    CLOUD = "cloud"


class SizeType(StrEnum):
    """Категории LLM по размеру.

    Attributes:
        TINY: Малые модели 1B-3B параметров.
        SMALL: Маленькие модели 7B-14B параметров.
        MEDIUM: Средние 20B-70B параметров.
        LARGE: Большие 130B-400B+ параметров.
    """

    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Rating(ValueObject):
    """Рейтинг модели"""

    count_of_usage: NonNegativeInt
    stars: NonNegativeInt


class TariffMethod(StrEnum):
    """Метод тарификации облачных решений.

    Attributes:
        PAY_AS_YOU_GO: На основе токенов (оплата по факту использования).
        SAAS: Подписка с фиксированной оплатой.
        SPOT_INSTANCE: На основе инфраструктуры (почасовая оплата GPU).
    """

    PAY_AS_YOU_GO = "pay-as-you-go"
    SAAS = "SaaS"
    SPOT_INSTANCE = "spot-instance"


class ModelCapability(StrEnum):
    """Возможности модели"""

    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    VISION = "vision"
    TRANSLATION = "translation"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"


class ModalityType(StrEnum):
    """Модальность модели (с какими данными работает модель)"""

    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class TargetDomain(StrEnum):
    """Доменные области для спецификации модели"""

    GENERAL_PURPOSE = "Общего назначения"
    CODE_GENERATION = "Генерация кода"
    MEDICAL = "Медицина"
    LEGAL = "Юридический"
    FINANCIAL = "Финансовый"
    SCIENTIFIC = "Научный"

    @classmethod
    def default(cls) -> set[str]:
        return {cls.GENERAL_PURPOSE.value()}


class SystemRequirements(ValueObject):
    """Системные требования.

    Attributes:
        cpu: Количество ядер CPU.
        ram: Количество ГБ ОЗУ.
        vram: Количество ГБ оперативной памяти GPU.
        ssd: Место на SSD диске в ГБ.
    """

    cpu: PositiveInt
    ram: PositiveInt
    vram: PositiveInt
    ssd: PositiveInt
