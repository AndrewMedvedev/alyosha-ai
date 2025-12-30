from uuid import UUID

from pydantic import SecretStr

from modules.shared_kernel.domain import Command

from .value_objects import SecretType


class StoreSecretCommand(Command):
    """Сохранение секрета"""

    user_id: UUID
    name: str
    description: str | None = None
    secret_type: SecretType
    secret_data: SecretStr
