from uuid import UUID

from pydantic import Field, SecretStr

from modules.shared_kernel.application import DTO

from ..domain import SecretType


class SecretCreate(DTO):
    """Создание секрета"""

    id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    secret_type: SecretType
    encrypted_data: str
    encryption_context: dict[str, str] = Field(default_factory=dict)


class EncryptedSecret(DTO):
    id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    secret_type: SecretType
    encrypted_data: str
    encryption_context: dict[str, str] = Field(default_factory=dict)


class SecretRevealed(DTO):
    """Раскрытый секрет"""

    id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    secret_type: SecretType
    secret_data: SecretStr
