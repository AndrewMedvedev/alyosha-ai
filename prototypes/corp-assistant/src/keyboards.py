from enum import StrEnum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AdminAction(StrEnum):
    UPLOAD_DOCUMENTS = "upload_documents"


class AdminMenuCBData(CallbackData, prefix="admin_menu"):
    user_id: int
    action: AdminAction


def get_admin_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💾 Загрузить документы",
        callback_data=AdminMenuCBData(user_id=user_id, action=AdminAction.UPLOAD_DOCUMENTS).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()
