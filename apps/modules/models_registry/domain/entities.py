from typing import Self

from abc import ABC

from pydantic import Field, HttpUrl, NonNegativeInt

from modules.shared_kernel.domain import Entity

from .commands import CreateEntryCommand
from .primitives import ModelSlug
from .value_objects import (
    DeploymentType,
    LLMCategory,
    ModelCapability,
    ModelModality,
    ModelSpecification,
    ModelTask,
    Rating,
    SizeType,
    TariffMethod,
)


def default_target_domain() -> set[str]:
    return {"Общего назначения"}


class BaseLLM(Entity, ABC):
    slug: ModelSlug
    name: str
    provider_name: str
    source_url: HttpUrl
    description: str
    size_type: SizeType
    category: LLMCategory
    capabilities: set[ModelCapability] = Field(default_factory=set)
    target_domains: set[str] = Field(default_factory=default_target_domain)
    rating: Rating


class OpenSourceLLM(BaseLLM):
    category: LLMCategory = Field(default=LLMCategory.OPEN_SOURCE, frozen=True)


class CommercialLLM(BaseLLM):
    category: LLMCategory = Field(default=LLMCategory.COMMERCIAL, frozen=True)
    tariff_method: TariffMethod


class ModelEntry(Entity):
    """Запись модели в каталоге"""

    slug: ModelSlug
    name: str
    provider_name: str
    source_url: HttpUrl | None = None
    description: str
    deployment_type: DeploymentType
    task: ModelTask
    capabilities: set[ModelCapability] = Field(default_factory=set)
    modality: ModelModality
    specification: ModelSpecification
    usage_count: NonNegativeInt = Field(default=0)
    stars: NonNegativeInt = Field(default=0)

    @classmethod
    def create(cls, command: CreateEntryCommand) -> Self:
        return cls.model_validate(command)
