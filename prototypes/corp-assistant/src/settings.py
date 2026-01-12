from typing import Final

from pathlib import Path

import pytz
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEZONE = pytz.timezone("Europe/Moscow")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: str = "<TOKEN>"


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


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELASTICSEARCH_")


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    yandexcloud: YandexCloudSettings = YandexCloudSettings()
    sber_devices: SberDevicesSettings = SberDevicesSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()


settings: Final[Settings] = Settings()
