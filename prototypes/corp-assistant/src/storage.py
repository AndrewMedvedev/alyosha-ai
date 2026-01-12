import logging
from pathlib import Path

import aiofiles

from .core.exceptions import FileDoesNotExistError
from .core.schemas import File
from .settings import PROJECT_ROOT

logger = logging.getLogger(__name__)

MEDIA_DIR = PROJECT_ROOT / ".media"
MEDIA_DIR.mkdir(exist_ok=True)


async def upload_file(file: File) -> None:
    async with aiofiles.open(file.path, mode="wb") as open_file:
        await open_file.write(file.data)
    logger.info("File uploaded to `%s`", file.path)


async def download_file(path: str) -> File:
    if not Path(path).exists():
        raise FileDoesNotExistError(f"File `{path}` does not exist!")
    async with aiofiles.open(path, mode="rb") as open_file:
        data = await open_file.read()
    logger.info("File downloaded from `%s`", path)
    return File.from_raw(path, data)
