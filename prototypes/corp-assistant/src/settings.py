from typing import Final

from pathlib import Path

import pytz
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEZONE = pytz.timezone("Europe/Moscow")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: str = "<TOKEN>"


class SberDevicesSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SBER_DEVICES_")

    apikey: str = "<APIKEY>"
    scope: str = "<SCOPE>"
    client_id: str = "<CLIENT_ID>"
    client_secret: str = "<CLIENT_SECRET>"


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    sber_devices: SberDevicesSettings = SberDevicesSettings()


settings: Final[Settings] = Settings()
