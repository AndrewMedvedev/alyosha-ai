from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from api.dependencies import PaginationDep
from modules.iam.domain import UserRole
from modules.iam.infrastructure.fastapi import require_user_roles
from modules.models_registry.application import CreateEntryUseCase, RegistryRepository
from modules.models_registry.domain import CreateEntryCommand, ModelEntry

router = APIRouter(prefix="/models-registry", tags=["Models registry"], route_class=DishkaRoute)

# Требуемые роли для модификации каталога моделей
REQUIRED_ROLES_FOR_MODIFY_CATALOG = {
    UserRole.MODERATOR, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPERADMIN
}


@router.post(
    path="/entries",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelEntry,
    dependencies=[Depends(require_user_roles(*REQUIRED_ROLES_FOR_MODIFY_CATALOG))],
    summary="Запись модели в каталог",
)
async def create_model_entry(
        command: CreateEntryCommand, usecase: FromDishka[CreateEntryUseCase]
) -> ModelEntry:
    return await usecase.execute(command)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=list[ModelEntry],
    summary="Просмотр каталога",
    description="Записи сортируются по популярности",
)
async def get_most_popular_registry_entries(
        pagination: PaginationDep, repository: FromDishka[RegistryRepository]
) -> list[ModelEntry]:
    return await repository.get_most_popular(pagination)
