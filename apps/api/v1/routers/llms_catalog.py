from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from api.dependencies import PaginationDep
from modules.iam.domain import UserRole
from modules.iam.infrastructure.fastapi import require_user_roles
from modules.llm_catalog.application import AddLLMToCatalogUseCase, CatalogRepository
from modules.llm_catalog.domain import AddAnyLLMToCatalogCommand, AnyLLM
from modules.shared_kernel.application.exceptions import NotFoundError

router = APIRouter(prefix="/llms-catalog", tags=["LLM catalog"], route_class=DishkaRoute)

# Требуемые роли для модификации каталога моделей
REQUIRED_ROLES_FOR_MODIFY_CATALOG = {
    UserRole.MODERATOR, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPERADMIN
}


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=AnyLLM,
    dependencies=[Depends(require_user_roles(*REQUIRED_ROLES_FOR_MODIFY_CATALOG))],
    summary="Запись модели в каталог",
)
async def add_llm_to_catalog(
        command: AddAnyLLMToCatalogCommand, usecase: FromDishka[AddLLMToCatalogUseCase]
) -> AnyLLM:
    return await usecase.execute(command)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=list[AnyLLM],
    summary="Просмотр каталога",
    description="Записи сортируются по популярности",
)
async def get_most_popular_llms(
        pagination: PaginationDep, repository: FromDishka[CatalogRepository]
) -> list[AnyLLM]:
    return await repository.get_most_popular(pagination)


@router.get(
    path="/{llm_id}",
    status_code=status.HTTP_200_OK,
    response_model=AnyLLM,
    summary="Получить конкретную LLM"
)
async def get_llm(llm_id: UUID, repository: FromDishka[CatalogRepository]) -> AnyLLM:
    llm = await repository.read(llm_id)
    if llm is None:
        raise NotFoundError(
            f"LLM not found in catalog by ID {llm_id}",
            entity_name="LLM",
            details={"llm_id": llm_id}
        )
    return llm
