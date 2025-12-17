from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    JsonField,
    TextNull,
    UUIDArray,
    UUIDField,
)


class MessageModel(Base):
    __tablename__ = "messages"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"), unique=False)
    ...

    chat: Mapped["ChatModel"] = relationship(back_populates="messages")


class ChatModel(Base):
    __tablename__ = "chats"

    ...
