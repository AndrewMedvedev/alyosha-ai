import io
import logging
from enum import StrEnum

import markdown
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sulguk import transform_html

from .ai_agent import Context, call_agent
from .core.schemas import UserRole
from .rag import rag_pipeline
from .services import users
from .services.minutes import create_minutes_task
from .settings import settings
from .utils import convert_document_to_md

logger = logging.getLogger(__name__)

session = AiohttpSession(
    api=TelegramAPIServer.from_base(settings.telegram.api_url, is_local=True)
)

bot = Bot(
    token=settings.telegram.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)

dp = Dispatcher(storage=MemoryStorage())


class MinutesForm(StatesGroup):
    """Форма для составления протокола совещания"""

    file_id = State()
    document_ext = State()


class Vote(StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class VoteCBData(CallbackData, prefix="vote"):
    user_id: int
    message_id: int
    vote: Vote


def get_voting_kb(user_id: int, message_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для оценки сообщения от AI ассистента"""

    builder = InlineKeyboardBuilder()
    builder.button(text="👍", callback_data=VoteCBData(
        user_id=user_id, message_id=message_id, vote=Vote.LIKE
    ).pack())
    builder.button(text="👎", callback_data=VoteCBData(
        user_id=user_id, message_id=message_id, vote=Vote.DISLIKE
    ).pack())
    builder.adjust(1)
    return builder.as_markup()


class AdminAction(StrEnum):
    ADD_DOCUMENTS = "add_documents"


class AdminMenuCBData(CallbackData, prefix="admin_menu"):
    user_id: int
    action: AdminAction


def get_admin_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📑 Загрузить документы",
        callback_data=AdminMenuCBData(user_id=user_id, action=AdminAction.ADD_DOCUMENTS).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


class AdminUploadForm(StatesGroup):
    """Форма для загрузки файлов админом"""

    upload_file = State()
    choose_next_step = State()


def get_admin_next_step_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Загрузить ещё")
    builder.button(text="Завершить")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_document_ext_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=".docx")
    builder.button(text=".pdf")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


@dp.message(CommandStart())
async def handle_start_cmd(message: Message) -> None:
    user_id = message.from_user.id
    if users.is_admin(user_id):
        admin = await users.get(user_id)
        if admin is None:
            await users.save(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                role=UserRole.ADMIN
            )
        await message.reply("Админ панель", reply_markup=get_admin_menu_kb(user_id))
        return
    user = await users.get(user_id)
    if user is None:
        await users.save(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    await message.reply(f"Добро пожаловать <b>{user.fist_name}</b>")


@dp.callback_query(AdminMenuCBData.filter(F.action == AdminAction.ADD_DOCUMENTS))
async def admin_menu_add_documents_handler(
        query: CallbackQuery, state: FSMContext
) -> None:
    await query.answer()
    if not users.is_admin(query.from_user.id):
        await query.message.answer("🚫 Недостаточно прав!")
        return
    await query.message.answer("📤 Отправьте документы (PDF, DOCX, PPTX). Можно несколько.")
    await state.set_state(AdminUploadForm.upload_file)


@dp.message(AdminUploadForm.upload_file, F.document)
async def process_admin_uploaded_document(message: Message, state: FSMContext) -> None:
    if not users.is_admin(message.from_user.id):
        await message.answer("🚫 Недостаточно прав!")
        return
    file_id, filename = message.document.file_id, message.document.file_name
    file = await bot.get_file(file_id)
    bot_message = await message.answer("Скачиваю файл ...")
    file_buffer = await bot.download_file(file.file_path, destination=io.BytesIO())
    data = file_buffer.getbuffer().tobytes()
    await bot_message.edit_text("Конвертирую в Markdown ...")
    md_text = convert_document_to_md(data, extension=f".{filename.split('.')[-1]}")
    await bot_message.edit_text("Добавляю в базу знаний ...")
    rag_pipeline.indexing(text=md_text, metadata={"source": filename})
    await bot.delete_message(bot_message.chat.id, bot_message.message_id)
    await message.answer(
        text="Файл успешно проиндексирован", reply_markup=get_admin_next_step_kb()
    )
    await state.set_state(AdminUploadForm.choose_next_step)


@dp.message(AdminUploadForm.choose_next_step, F.text)
async def process_admin_next_step(message: Message, state: FSMContext) -> None:
    if not users.is_admin(message.from_user.id):
        await message.answer("🚫 Недостаточно прав!")
        return
    if message.text == "Загрузить ещё":
        await message.answer("📤 Отправьте документ (PDF, DOCX, PPTX).")
        await state.set_state(AdminUploadForm.choose_next_step)
    elif message.text == "Завершить":
        await message.answer("Завершаю цикл")
        await state.clear()
    return


@dp.message(Command("minutes"))
async def handle_minutes_cmd(message: Message, state: FSMContext) -> None:
    await message.answer("Отправьте аудио файл или голосовое сообщение")
    await state.set_state(MinutesForm.file_id)


@dp.message(MinutesForm.file_id, F.voice | F.audio)
async def process_audio_file(message: Message, state: FSMContext) -> None:
    if message.audio:
        file_id = message.audio.file_id
        logger.info("Received audio file %s", message.audio.file_name)
    elif message.voice:
        file_id = message.voice.file_id
        logger.info("Received voice message with duration %s", message.voice.duration)
    else:
        await message.answer("❌ Пожалуйста, отправьте аудио файл или голосовое сообщение")
        return
    await state.update_data(file_id=file_id)
    await message.answer(
        text="Выберите файл в котором вам удобнее получить протокол",
        reply_markup=get_document_ext_kb()
    )
    await state.set_state(MinutesForm.document_ext)


@dp.message(MinutesForm.document_ext, F.text)
async def process_document_ext_choice(message: Message, state: FSMContext) -> None:
    document_ext = message.text
    logger.info("User choose %s document extension as output format", document_ext)
    await state.update_data(document_ext=document_ext)
    data = await state.get_data()
    await message.answer("Данные переданы ассистенту", reply_markup=ReplyKeyboardRemove())
    await create_minutes_task(
        user_id=message.from_user.id,
        file_ids=[data["file_id"]],
        document_ext=document_ext,
    )


@dp.message()
async def handle_message(message: Message) -> None:
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        ai_message = await call_agent(
            message_text=message.text,
            context=Context(
                user_id=message.from_user.id, first_name=message.from_user.first_name
            )
        )
    result = transform_html(markdown.markdown(ai_message))
    await message.reply(text=result.text, entities=result.entities)
