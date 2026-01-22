import logging
from enum import StrEnum

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..keyboards import AdminAction, AdminMenuCBData, get_admin_menu_kb
from ..rag import rag_pipeline
from ..utils import convert_document_to_md

logger = logging.getLogger(__name__)

router = Router(name=__name__)


class NextStep(StrEnum):
    ADD_MORE = "add_more"
    FINISH = "finish"


class NextStepCBData(CallbackData, prefix="next_step"):
    next_step: NextStep


class UploadForm(StatesGroup):
    """Форма для загрузки файлов админом"""

    waiting_for_documents = State()
    in_next_step_choice = State()


def get_next_step_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Добавить ещё",
        callback_data=NextStepCBData(next_step=NextStep.ADD_MORE).pack()
    )
    builder.button(
        text="🏁 Завершить загрузку",
        callback_data=NextStepCBData(next_step=NextStep.FINISH).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(AdminMenuCBData.filter(F.action == AdminAction.UPLOAD_DOCUMENTS))
async def cb_upload_documents(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await query.answer("Загрузите файлы")
    await state.set_state(UploadForm.waiting_for_documents)


@router.message(UploadForm.waiting_for_documents, F.document)
async def process_uploaded_documents(message: Message, state: FSMContext) -> None:
    file_info = await message.bot.get_file(message.document.file_id)
    file = await message.bot.download_file(file_info.file_path)
    data = file.getbuffer().tobytes()
    logger.info(
        "Document `%s` downloaded from telegram, size %s mb",
        file_info.file_path, round(len(data) / 1_000_000, 2),
    )
    md_content = convert_document_to_md(
        data, extension=f".{message.document.file_name.split('.')[-1]}"
    )
    rag_pipeline.indexing(md_content, metadata={"source": message.document.file_name})
    await message.answer(
        text=f"Документ <b>{message.document.file_name}</b> успешно проиндексирован",
        reply_markup=get_next_step_kb(),
    )
    await state.set_state(UploadForm.in_next_step_choice)


@router.callback_query(
    UploadForm.in_next_step_choice,
    NextStepCBData.filter(F.next_step == NextStep.ADD_MORE)
)
async def cb_add_more_documents(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await query.answer("Загрузите файлы")
    await state.set_state(UploadForm.waiting_for_documents)


@router.callback_query(
    UploadForm.in_next_step_choice,
    NextStepCBData.filter(F.next_step == NextStep.FINISH)
)
async def cb_finish_uploading(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await query.answer(
        text="Загрузка завершена", reply_markup=get_admin_menu_kb(query.from_user.id)
    )
    await state.clear()
