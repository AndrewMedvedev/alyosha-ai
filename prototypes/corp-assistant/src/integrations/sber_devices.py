import logging
from uuid import uuid4

import aiohttp

from ..settings import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/"


class SberDevicesError(Exception):
    pass


class AuthenticationError(SberDevicesError):
    """Ошибка аутентификации"""


async def authenticate(use_ssl: bool = False) -> str:
    """Производит аутентификацию клиента, выдавая access token"""

    rq_uid = uuid4()
    headers = {
        "Authorization": f"Bearer {settings.sber_devices.apikey}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": f"{rq_uid}",
    }
    payload = {"scope": settings.sber_devices.scope}
    try:
        async with aiohttp.ClientSession(base_url=BASE_URL) as session, session.post(
            url="/oauth", headers=headers, data=payload, ssl=use_ssl
        ) as response:
            response.raise_for_status()
            data = await response.json()
        access_token = data.get("access_token")
        if access_token is None:
            error_message = "Authentication failed, access token missing in response!"
            logger.error(error_message)
            raise AuthenticationError(error_message)
    except aiohttp.ClientResponseError as e:
        error_message = f"Authentication failed with status {response.status}, error: {e}"
        logger.exception(error_message)
        raise AuthenticationError(error_message) from e
    except aiohttp.ClientError as e:
        error_message = f"An unexpected error occurred while authentication, error {e}"
        logger.exception(error_message)
        raise AuthenticationError(error_message) from e
    else:
        logger.info("Client successfully authenticated!")
        return access_token
