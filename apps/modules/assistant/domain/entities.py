from uuid import UUID

from pydantic import Field

from modules.shared_kernel.domain import Entity

from .value_objects import IntegrationConfig, IntegrationStatus


class LLMIntegration(Entity):
    workspace_id: UUID
    name: str
    description: str | None = None
    status: IntegrationStatus
    config: IntegrationConfig


class Assistant(Entity):
    workspace_id: UUID
    name: str
    system_prompt: str
    connected_agents: list[UUID] = Field(default_factory=list)
