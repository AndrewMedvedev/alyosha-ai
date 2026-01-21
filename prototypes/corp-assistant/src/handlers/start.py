from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from ..core import schemas
from ..database import crud, models
from ..keyboards import get_admin_menu_kb
from ..service import is_admin
from ..settings import settings

router = Router(name=__name__)

WELCOME_MESSAGE = f"""Добрый день,
я ваш корпоративный ассистент - <b>{settings.assistant.name}</b>.
Я могу составить протокол совещания, а также найти ответ на вопрос по внутренней документации.
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        admin = await crud.read(user_id, model_class=models.User, schema_class=schemas.User)
        if admin is None:
            admin = schemas.User(
                id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                role=schemas.UserRole.ADMIN,
            )
            await crud.create(admin, model_class=models.User)
        await message.reply(WELCOME_MESSAGE, reply_markup=get_admin_menu_kb(user_id))
        return
    user = await crud.read(user_id, model_class=models.User, schema_class=schemas.User)
    if user is None:
        user = schemas.User(
            id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            role=schemas.UserRole.USER,
        )
        await crud.create(user, model_class=models.User)
    await message.reply(WELCOME_MESSAGE)
