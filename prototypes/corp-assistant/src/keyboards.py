from enum import StrEnum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AdminAction(StrEnum):
    UPLOAD_DOCUMENTS = "upload_documents"


class AdminMenuCBData(CallbackData, prefix="admin_menu"):
    user_id: int
    action: AdminAction


def get_admin_menu_kb(webapp_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💾 Загрузить документы",
        web_app=WebAppInfo(url=webapp_url),
    )
    builder.adjust(1)
    return builder.as_markup()
