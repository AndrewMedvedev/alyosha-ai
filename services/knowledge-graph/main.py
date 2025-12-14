import asyncio
import logging
from collections.abc import AsyncIterable
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)

WORKDIR = Path.cwd() / "workflow"


async def upload_document(filename: str, content: AsyncIterable[bytes]) -> Path:
    path = Path(filename)
    slug = path.stem
    filepath = WORKDIR / slug / f"input{path.suffix}"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(filepath, mode="wb") as file:
        async for chunk in content:
            await file.write(chunk)
    return filepath


async def main() -> None:
    filename = "НИР_Косов Андрей Сергеевич.docx"
    chunk_size = 8192

    async with aiofiles.open(filename, mode="rb") as file:

        async def chunk_generator() -> AsyncIterable[bytes]:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        uploaded_path = await upload_document(filename, chunk_generator())
        logger.info("File uploaded %s", filename)
        logger.info("Absolute path %s", uploaded_path)
        logger.info("File size %s of bytes", uploaded_path.stat().st_size)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
