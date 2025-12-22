from modules.shared_kernel.application import UnitOfWork

from ..domain import (
    AddAnyLLMToCatalogCommand,
    AddCommercialLLMToCatalogCommand,
    AnyLLM,
    CommercialLLM,
    OpenSourceLLM,
)
from .repository import CatalogRepository


def llm_item_factory(command: AddAnyLLMToCatalogCommand) -> AnyLLM:
    if isinstance(command, AddCommercialLLMToCatalogCommand):
        return CommercialLLM.create(command)
    return OpenSourceLLM.create(command)


class AddLLMToCatalogUseCase:
    def __init__(self, uow: UnitOfWork, repository: CatalogRepository) -> None:
        self._uow = uow
        self._repository = repository

    async def execute(self, command: AddAnyLLMToCatalogCommand) -> AnyLLM:
        async with self._uow.transactional() as uow:
            llm = llm_item_factory(command)
            print(llm)
            await self._repository.create(llm)
            await uow.commit()
        return llm
