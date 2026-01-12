from langchain.tools import tool
from pydantic import BaseModel, Field, PositiveInt

from .. import rag


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
