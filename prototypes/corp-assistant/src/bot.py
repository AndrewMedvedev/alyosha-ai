from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .handlers import router
from .settings import settings

session = AiohttpSession(api=TelegramAPIServer.from_base(settings.telegram.api_url, is_local=True))

bot = Bot(
    token=settings.telegram.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)
