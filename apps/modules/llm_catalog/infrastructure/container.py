from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared_kernel.application import UnitOfWork

from ..application import AddLLMToCatalogUseCase, CatalogRepository
from .database import SQLAlchemyCatalogRepository


class LLMCatalogProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_catalog_repo(self, session: AsyncSession) -> CatalogRepository:  # noqa: PLR6301
        return SQLAlchemyCatalogRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_llm_to_catalog_addition_usecase(  # noqa: PLR6301
            self, uow: UnitOfWork, repository: CatalogRepository
    ) -> AddLLMToCatalogUseCase:
        return AddLLMToCatalogUseCase(uow=uow, repository=repository)
