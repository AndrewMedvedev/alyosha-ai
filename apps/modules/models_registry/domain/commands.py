from pydantic import Field

from modules.shared_kernel.domain import Command

from .primitives import ModelSlug
from .value_objects import (
    DeploymentType,
    ModelCapability,
    ModelModality,
    ModelSpecification,
    ModelTask,
)


class CreateEntryCommand(Command):
    """Создание записи в каталоге"""

    slug: ModelSlug = Field(
        ..., description="Идентификатор модели", examples=["google/gemma-7b"]
    )
    name: str = Field(..., description="Название модели", examples=["Gemma"])
    provider_name: str = Field(..., description="Провайдер модели", examples=["Google"])
    source_url: str = Field(
        default=None, description="URL источника", examples=["https://google.com"]
    )
    description: str = Field(..., description="Описание модели с свободном формате")
    deployment_type: DeploymentType
    task: ModelTask
    capabilities: set[ModelCapability] = Field(default_factory=set)
    modality: ModelModality
    specification: ModelSpecification
