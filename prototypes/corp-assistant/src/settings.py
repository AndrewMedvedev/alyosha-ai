from typing import Final, Literal

from pathlib import Path

import pytz
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEZONE = pytz.timezone("Europe/Moscow")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
ENV_PATH = PROJECT_ROOT / ".env"
CHROMA_PATH = PROJECT_ROOT / ".chroma"
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ENV_PATH)


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")

    bot_token: str = "<BOT TOKEN>"
    api_id: str = "<API ID>"
    api_hash: str = "<API HASH>"
    api_port: int = 8081
    api_host: str = "localhost"
    bot_admin_id: int = -1

    @property
    def api_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}"


class YandexCloudSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YANDEX_CLOUD_")

    folder_id: str = "<FOLDER_ID>"
    apikey: str = "<APIKEY>"
    base_url: str = "https://llm.api.cloud.yandex.net/v1"

    @property
    def gemma_3_27b_it(self) -> str:
        return f"gpt://{self.folder_id}/gemma-3-27b-it/latest"

    @property
    def aliceai_llm(self) -> str:
        return f"gpt://{self.folder_id}/aliceai-llm"

    @property
    def qwen3_235b(self) -> str:
        return f"gpt://{self.folder_id}/qwen3-235b-a22b-fp8/latest"

    @property
    def yandexgpt_rc(self) -> str:
        return f"gpt://{self.folder_id}/yandexgpt/rc"


class SberDevicesSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SBER_DEVICES_")

    apikey: str = "<APIKEY>"
    scope: str = "<SCOPE>"
    client_id: str = "<CLIENT_ID>"
    client_secret: str = "<CLIENT_SECRET>"


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    host: str = "postgres"
    port: int = 5432
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    db: str = "<DB>"
    driver: Literal["asyncpg"] = "asyncpg"

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "redis"
    port: str = "6379"

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/0"


class AssistantSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASSISTANT_")

    platform: str = ""
    name: str = "Алексей"
    company_name: str = "ДИО-Консалт"
    company_website: str = "<Web-сайт компании>"
    company_description: str = "<Описание деятельности компании>"


class Settings(BaseSettings):
    base_url: str = ""
    telegram: TelegramSettings = TelegramSettings()
    yandexcloud: YandexCloudSettings = YandexCloudSettings()
    sber_devices: SberDevicesSettings = SberDevicesSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    assistant: AssistantSettings = AssistantSettings()


settings: Final[Settings] = Settings()
