from enum import StrEnum


class SecretType(StrEnum):
    """Тип хранимого секрета"""

    APIKEY = "apikey"
    OAUTH_TOKEN = "oauth-token"
    PASSWORD = "password"
