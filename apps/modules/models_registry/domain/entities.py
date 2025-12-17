from typing import Self

from pydantic import Field, HttpUrl, NonNegativeInt

from modules.shared_kernel.domain import Entity

from .commands import CreateEntryCommand
from .primitives import ModelSlug
from .value_objects import (
    DeploymentType,
    ModelCapability,
    ModelModality,
    ModelSpecification,
    ModelTask,
)


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
