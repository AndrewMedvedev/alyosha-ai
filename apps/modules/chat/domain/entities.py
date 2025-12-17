from uuid import UUID

from pydantic import Field, NonNegativeInt, computed_field

from modules.shared_kernel.domain import AggregateRoot, Entity

from .value_objects import ContentBlock, MessageMetadata, MessageRole


class Message(Entity):
    """Сообщение внутри чата.

    Attributes:
        chat_id: Идентификатор чата.
        sender_id: Идентификатор отправителя сообщения (user_id или assistant_id).
        role: Роль сообщения (`system`, `assistant`, `user`).
        content_blocks: Блоки с контентом.
        metadata: Метаданные сообщения.
    """

    chat_id: UUID
    sender_id: UUID
    role: MessageRole
    content_blocks: list[ContentBlock] = Field(default_factory=list)
    metadata: MessageMetadata


class Conversation(Entity):
    """Текущая беседа с пользователем - N сообщений (например текущий день)"""

    title: str | None = None
    messages: list[Message] = Field(default_factory=list)

    @computed_field(description="Длина беседы")
    def length(self) -> NonNegativeInt:
        return len(self.messages)

    def to_markdown(self) -> str: ...


class Chat(AggregateRoot):
    """Индивидуальная чат-сессия для каждого из пользователей.

    Attributes:
        workspace_id: Идентификатор рабочего пространства.
        user_id: Идентификатор пользователя, для которого создана сессия.
        title: Название чата (тема чата, может генерироваться AI).
        description: Описание сути чата (для общего понимания контекста).
        messages_count: Общее количество сообщений в чате.
        conversation: Текущие сообщения в беседе (например на сегодняшний день).
    """

    workspace_id: UUID
    user_id: UUID
    title: str
    description: str | None = None
    messages_count: NonNegativeInt
    conversation: Conversation
