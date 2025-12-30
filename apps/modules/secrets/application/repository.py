from uuid import UUID

from ..domain import SecretReference
from .dto import EncryptedSecret, SecretCreate


class SecretRepository:
    async def create(self, secret_creation: SecretCreate) -> SecretReference: ...

    async def read(self, secret_id: UUID) -> EncryptedSecret: ...
