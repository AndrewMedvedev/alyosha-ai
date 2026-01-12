from aiogram.types import ContentType
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, PositiveInt

from .. import rag
from ..settings import PROMPTS_DIR, settings


class AssistantContext(BaseModel):
    """Контекст работы корпоративного AI ассистента"""

    user_id: PositiveInt


class AssistantState(AgentState):
    """Текущее состояние ассистента"""

    message_id: int
    content_type: ContentType


class RAGSearchInput(BaseModel):
    """Описание входных аргументов для RAG-поиска"""

    search_query: str = Field(
        description="Запрос для поиска релевантных документов"
    )
    top_k: PositiveInt = Field(
        default=10, description="Количество извлекаемых документов"
    )


@tool(
    "search_in_knowledge_base",
    description="Выполняет поиск информации во внутренней базе знаний",
    args_schema=RAGSearchInput,
)
async def rag_search(search_query: str, top_k: int = 10) -> str:
    """Выполняет поиск информации во внутренней базе знаний"""

    documents = await rag.retrieve_documents(search_query, top_k=top_k)
    return "\n\n".join(documents)


model = ChatOpenAI(
    api_key=settings.yandexcloud.apikey,
    model=settings.yandexcloud.yandexgpt_rc,
    base_url=settings.yandexcloud.base_url,
    temperature=0.5,
    max_retries=3
)

system_prompt = (PROMPTS_DIR / "system_prompt.md").read_text(encoding="utf-8")

summary_prompt = (PROMPTS_DIR / "summary_prompt.md").read_text(encoding="utf-8")

summarization_middleware = SummarizationMiddleware(
    model=ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3
    ),
    trigger=...,
    summary_prompt=summary_prompt
)

agent = create_agent(
    model=model,
    system_prompt=system_prompt,
    context_schema=AssistantContext,
    state_schema=AssistantState,
    tools=[rag_search],
    middleware=[summarization_middleware],
    checkpointer=...,
)
