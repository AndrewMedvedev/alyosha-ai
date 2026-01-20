from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from ..keyboards import AdminAction, AdminMenuCBData
from ..service import is_admin

router = Router(name=__name__)


class AdminUploadForm(StatesGroup):
    """Форма для загрузки файлов админом"""

    waiting_document = State()
    in_next_step_choice = State()


def get_admin_next_step_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ Добавить ещё")
    builder.button(text="🏁 Завершить загрузку")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
