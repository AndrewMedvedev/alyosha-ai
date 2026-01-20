from ..core import schemas
from ..database import crud, models
from ..settings import settings


async def get(user_id: int) -> schemas.User | None:
    return await crud.read(user_id, model_class=models.User, schema_class=schemas.User)


async def save(
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        role: schemas.UserRole = schemas.UserRole.USER
) -> schemas.User:
    user = schemas.User(
        id=user_id,
        username=username,
        fist_name=first_name,
        last_name=last_name,
        role=role
    )
    await crud.create(user, model_class=models.User)
    return user


def is_admin(user_id: int) -> bool:
    return user_id == settings.telegram.bot_admin_id
