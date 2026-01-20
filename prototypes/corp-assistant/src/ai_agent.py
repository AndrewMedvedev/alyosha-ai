from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, SummarizationMiddleware, dynamic_prompt
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import AsyncRedisSaver
from pydantic import BaseModel, Field, PositiveInt

from .rag import rag_pipeline
from .settings import PROMPTS_DIR, settings
from .utils import current_datetime


class Context(BaseModel):
    """Контекст работы корпоративного AI ассистента"""

    user_id: PositiveInt
    first_name: str


class RAGSearchInput(BaseModel):
    """Описание входных аргументов для RAG-поиска"""

    search_query: str = Field(
        description="Запрос для поиска информации"
    )
    source: str | None = Field(
        default=None,
        description="""Файл в котором нужно искать информацию
        (указывай его если только ты знаешь его точное имя)"""
    )
    n_results: PositiveInt = Field(
        default=10, description="Количество извлекаемых документов"
    )


@tool(
    "search_in_knowledge_base",
    description="Выполняет поиск информации во внутренней базе знаний",
    args_schema=RAGSearchInput,
)
def rag_search(search_query: str, source: str | None = None, n_results: int = 10) -> str:
    """Выполняет поиск информации во внутренней базе знаний"""

    metadata_filter: dict[str, str] | None = None
    if source is not None:
        metadata_filter = {"source": source}
    documents = rag_pipeline.retrieve(
        search_query, metadata_filter=metadata_filter, n_results=n_results
    )
    return "\n\n".join(documents)


model = ChatOpenAI(
    api_key=settings.yandexcloud.apikey,
    model=settings.yandexcloud.qwen3_235b,
    base_url=settings.yandexcloud.base_url,
    temperature=0.5,
    max_retries=3
)

# Шаблон системного промпта AI ассистента
system_prompt = (PROMPTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
# Промпт для суммаризации истории чата
summary_prompt = (PROMPTS_DIR / "summary_prompt.md").read_text(encoding="utf-8")


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    """Динамический системный промпт с информацией о компании и пользователе"""

    return system_prompt.format(
        current_datetime=current_datetime(),
        platform=settings.assistant.platform,
        assistant_name=settings.assistant.name,
        company_name=settings.assistant.company_name,
        company_website=settings.assistant.company_website,
        company_description=settings.assistant.company_description,
        first_name=request.runtime.context.first_name,
    )


summarization_middleware = SummarizationMiddleware(
    model=ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3
    ),
    trigger=("tokens", 4000),
    keep=("messages", 20),
    summary_prompt=summary_prompt
)


async def call_agent(message_text: str, context: Context) -> str:
    async with AsyncRedisSaver.from_conn_string(
            settings.redis.url, ttl={"default_ttl": 60, "refresh_on_read": True}
    ) as checkpointer:
        await checkpointer.setup()
        agent = create_agent(
            model=model,
            context_schema=Context,
            tools=[rag_search],
            middleware=[dynamic_system_prompt, summarization_middleware],
            checkpointer=checkpointer,
        )
        config = {"configurable": {"thread_id": f"{context.user_id}"}}
        result = await agent.ainvoke(
            {"messages": [("human", message_text)]}, config=config, context=context
        )
    return result["messages"][-1].content
