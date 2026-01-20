__all__ = ("router",)

from aiogram import Router

from .chat import router as chat_router
from .minutes import router as minutes_router
from .start import router as start_router

router = Router()

router.include_routers(start_router, minutes_router, chat_router)
