import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .bot import bot, dp
from .broker import app as faststream_app
from .rag import rag_pipeline
from .service import is_admin
from .settings import BASE_DIR
from .utils import convert_document_to_md

logger = logging.getLogger(__name__)

WEBHOOK_URL = "http://localhost:8000/hook"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await faststream_app.broker.start()  # type: ignore
    await bot.set_webhook(
        url=WEBHOOK_URL, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True
    )
    logger.info("Telegram Bot webhook set to %s", WEBHOOK_URL)
    yield
    await bot.delete_webhook()
    logger.info("Telegram Bot webhook removed")
    await faststream_app.broker.stop()  # type: ignore


app = FastAPI(lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.post("/hook")
async def handle_aiogram_bot_update(request: Request) -> None:
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot=bot, update=update)


@app.post(
    path="/api/v1/documents/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка документов в базу знаний",
)
async def upload_documents(request: Request, files: list[UploadFile] = File(...)) -> None:
    user_id = request.headers.get("X-User-ID")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-User-ID header"
        )
    if not is_admin(int(user_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    for file in files:
        logger.info("Start indexing document: `%s`", file.filename)
        file_data = await file.read()
        file_extension = file.filename.split(".")[-1]
        md_content = convert_document_to_md(file_data, extension=f".{file_extension}")
        rag_pipeline.indexing(md_content, metadata={"source": file.filename})
    logger.info("Finish indexing documents")
