from uuid import UUID

from modules.shared_kernel.domain import Entity

from .value_objects import SecretType


class SecretReference(Entity):
    user_id: UUID
    name: str
    description: str
    secret_type: SecretType
