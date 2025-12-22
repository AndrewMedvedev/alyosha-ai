from pydantic import Field, PositiveInt

from modules.shared_kernel.domain import Command

from .primitives import ModelSlug
from .value_objects import (
    LLMCategory,
    ModalityType,
    ModelCapability,
    SystemRequirements,
    TargetDomain,
    TariffMethod,
)


class AddLLMToCatalogCommand(Command):
    """Заполнение общих полей LLM для записи в каталог моделей"""

    slug: ModelSlug = Field(
        ..., description="Идентификатор модели", examples=["google/gemma-7b"]
    )
    name: str = Field(..., description="Название модели", examples=["Gemma"])
    provider_name: str = Field(..., description="Провайдер модели", examples=["Google"])
    source_url: str = Field(
        default=None, description="URL источника", examples=["https://google.com"]
    )
    description: str = Field(..., description="Описание модели с свободном формате")
    billion_params_count: PositiveInt = Field(
        ..., description="Количество параметров модели в `B`"
    )
    context_window_tokens: PositiveInt = Field(
        ..., description="Длина контекстного окна в токенах"
    )
    category: LLMCategory = Field(..., description="Категория модели по типу доступа")
    modality: ModalityType = Field(..., description="Модальность модели")
    capabilities: set[ModelCapability] = Field(
        default_factory=set, description="Возможности модели"
    )
    target_domains: set[str] = Field(
        default_factory=TargetDomain.default,
        description="Задачи для которых предназначена LLM (по предметной области)"
    )


class AddOpenSourceLLMToCatalogCommand(AddLLMToCatalogCommand):
    """Добавление open-source модели в общий каталог"""

    min_system_requirements: SystemRequirements
    recommended_system_requirements: SystemRequirements


class AddCommercialLLMToCatalogCommand(AddLLMToCatalogCommand):
    """Добавление коммерческой модели в общий каталог"""

    tariff_method: TariffMethod


AddAnyLLMToCatalogCommand = AddCommercialLLMToCatalogCommand | AddOpenSourceLLMToCatalogCommand
