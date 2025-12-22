from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared_kernel.application import UnitOfWork
from modules.shared_kernel.application.message_bus import LogMessageBus

from ..application import CreateWorkspaceUseCase, WorkspaceRepository
from .database import SQLAlchemyWorkspaceRepository


class WorkspaceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_workspace_repo(self, session: AsyncSession) -> WorkspaceRepository:  # noqa: PLR6301
        return SQLAlchemyWorkspaceRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_workspace_creation_usecase(  # noqa: PLR6301
            self, uow: UnitOfWork, workspace_repo: WorkspaceRepository
    ) -> CreateWorkspaceUseCase:
        return CreateWorkspaceUseCase(
            uow=uow, repository=workspace_repo, message_bus=LogMessageBus()
        )
