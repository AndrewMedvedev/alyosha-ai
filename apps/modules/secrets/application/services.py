import json
from uuid import UUID, uuid4

from pydantic import SecretStr

from modules.iam.domain.exceptions import PermissionDeniedError
from modules.shared_kernel.application import UnitOfWork

from ..domain import SecretReference, StoreSecretCommand
from ..utils import string_encryptor
from .dto import SecretCreate, SecretRevealed
from .repository import SecretRepository


class SecretManagementService:
    def __init__(self, uow: UnitOfWork, repository: SecretRepository) -> None:
        self._uow = uow
        self._repository = repository

    async def store_secret(self, command: StoreSecretCommand) -> SecretReference:
        async with self._uow.transactional() as uow:
            secret_id = uuid4()
            context = {"user_id": f"{command.user_id}"}
            encrypted_data = string_encryptor.encrypt(
                string=command.secret_data.get_secret_value(), context=json.dumps(context)
            )
            secret_creation = SecretCreate(
                id=secret_id,
                user_id=command.user_id,
                name=command.name,
                description=command.description,
                secret_type=command.secret_type,
                encrypted_data=encrypted_data,
                encryption_context=context,
            )
            secret_reference = await self._repository.create(secret_creation)
            await uow.commit()
        return secret_reference

    async def reveal_secret(self, secret_id: UUID, user_id: UUID) -> SecretRevealed:
        encrypted_secret = await self._repository.read(secret_id)
        if user_id != encrypted_secret.user_id:
            raise PermissionDeniedError("Access denied!", details={"user_id": user_id})
        decrypted_data = string_encryptor.decrypt(
            encrypted_string=encrypted_secret.encrypted_data,
            context=json.dumps(encrypted_secret.encryption_context)
        )
        return SecretRevealed(
            id=encrypted_secret.id,
            user_id=encrypted_secret.user_id,
            name=encrypted_secret.name,
            description=encrypted_secret.description,
            secret_type=encrypted_secret.secret_type,
            secret_data=SecretStr(decrypted_data),
        )

    async def remove_secret(self) -> ...: ...
