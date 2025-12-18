from typing import Literal

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


class ModelTask(StrEnum):
    """Задачи выполняемые моделью"""

    IMAGE2TEXT = "image-to-text"
    STT = "speech-to-text"
    TTS = "text-to-speech"
    QA = "question-answering"
    ANY2ANY = "any2any"


class ModelModality(StrEnum):
    """Модальность модели (с какими данными работает модель)"""

    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class ModelSpecification(ValueObject):
    """Технические характеристики модели

    Attributes:
        params_count: Количество параметров.
        max_sequence_length: Максимальная длина контекста.
    """

    unit_of_params: Literal["M", "B"]
    params_count: PositiveInt
    max_sequence_length: PositiveInt
