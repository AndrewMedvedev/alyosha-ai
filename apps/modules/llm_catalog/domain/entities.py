from typing import Self, TypeVar

from abc import ABC
from datetime import datetime

from pydantic import Field, HttpUrl, PositiveInt

from modules.shared_kernel.domain import Entity

from .commands import AddLLMToCatalogCommand
from .primitives import ModelSlug
from .value_objects import (
    LLMCategory,
    ModalityType,
    ModelCapability,
    Rating,
    SizeType,
    SystemRequirements,
    TargetDomain,
    TariffMethod,
)


class BaseLLM(Entity, ABC):
    """Базовая LLM из общего каталога моделей.

    Attributes:
        slug: Идентификатор модели, например: `google/gemma-7b`.
        name: Название модели.
        provider_name: Название поставщика модели.
        source_url: URL адрес источника LLM.
        release_date: Дата релиза.
        description: Описание модели.
        size_type: Тип модели по её размеру.
        billion_params_count: Количество параметров LLM в `B`.
        context_window_tokens: Размер контекстного окна в токенах.
        category: Категория `open-source` и `commercial`.
        capabilities: Список возможностей модели.
        modality: Модальность с которой работает LLM.
        target_domains: Список областей для которых подходит модель.
        rating: Рейтинг модели (ставят пользователи).
    """

    slug: ModelSlug
    name: str
    provider_name: str
    source_url: HttpUrl
    release_date: datetime | None = None
    description: str
    size_type: SizeType
    billion_params_count: PositiveInt
    context_window_tokens: PositiveInt
    category: LLMCategory
    capabilities: set[ModelCapability] = Field(default_factory=set)
    modality: ModalityType
    target_domains: set[str] = Field(default_factory=TargetDomain.default)
    rating: Rating

    @staticmethod
    def _define_size_type(billion_params_count: int) -> SizeType:
        """Определение размера модели по количеству параметров"""

        if billion_params_count in range(1, 4):
            size_type = SizeType.TINY
        elif billion_params_count in range(7, 15):
            size_type = SizeType.SMALL
        elif billion_params_count in range(20, 71):
            size_type = SizeType.MEDIUM
        else:
            size_type = SizeType.LARGE
        return size_type

    @classmethod
    def create(cls, command: AddLLMToCatalogCommand) -> Self:
        return cls.model_validate({
            **command.model_dump(),
            "size_type": cls._define_size_type(command.billion_params_count),
            "rating": Rating(count_of_usage=0, stars=0),
        })


class OpenSourceLLM(BaseLLM):
    """LLM с открытым исходным кодом, доступна для скачивания и локального развёртывания.

    Attributes:
        min_system_requirements: Минимальные системные требования.
        recommended_system_requirements: Рекомендуемые системные требования.
    """

    category: LLMCategory = Field(default=LLMCategory.OPEN_SOURCE, frozen=True)
    min_system_requirements: SystemRequirements
    recommended_system_requirements: SystemRequirements


class CommercialLLM(BaseLLM):
    """LLM для коммерческого использования, доступна только по оплате.

    Attributes:
        tariff_method: Метод/способ тарификации.
    """

    category: LLMCategory = Field(default=LLMCategory.COMMERCIAL, frozen=True)
    tariff_method: TariffMethod


AnyLLM = OpenSourceLLM | CommercialLLM
AnyLLMT = TypeVar("AnyLLMT", bound=AnyLLM)
LLMsRegistryItems = TypeVar("LLMsRegistryItems", bound=list[AnyLLM])
