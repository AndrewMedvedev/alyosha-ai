import markdown
from aiogram import F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from ..ai_agent import Context, call_agent
from ..utils import escape_md2, transform_html

router = Router(name=__name__)


@router.message(F.text)
async def handle_message(message: Message) -> None:
    from ..bot import bot  # noqa: PLC0415

    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
        ai_content = await call_agent(
            message_text=message.text,
            context=Context(
                user_id=message.from_user.id, first_name=message.from_user.first_name
            )
        )
    md_text = transform_html(markdown.markdown(ai_content))
    await message.reply(text=escape_md2(md_text), parse_mode=ParseMode.MARKDOWN_V2)
