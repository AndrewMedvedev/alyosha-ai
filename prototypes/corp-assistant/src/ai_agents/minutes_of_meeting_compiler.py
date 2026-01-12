from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..settings import PROMPTS_DIR, settings

model = ChatOpenAI(
    api_key=settings.yandexcloud.apikey,
    model=settings.yandexcloud.qwen3_235b,
    base_url=settings.yandexcloud.base_url,
    temperature=0.2,
    max_retries=3
)

prompt = ChatPromptTemplate.from_template(
    (PROMPTS_DIR / "minutes_of_meeting_prompt.md").read_text(encoding="utf-8")
)

agent = prompt | model | StrOutputParser()
