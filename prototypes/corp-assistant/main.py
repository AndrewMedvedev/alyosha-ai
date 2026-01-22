import logging
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles

from src.api import app

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )


if __name__ == "__main__":
    configure_logging()
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
