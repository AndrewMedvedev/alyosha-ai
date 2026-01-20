from .settings import settings


def is_admin(user_id: int) -> bool:
    return user_id == settings.telegram.bot_admin_id
