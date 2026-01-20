FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY requirements-prod.txt .

RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install --no-cache-dir -r requirements-prod.txt

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Копируем только нужные runtime-зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем виртуальное окружение из builder
COPY --from=builder /venv /venv

COPY . .

# Создаём непривилегированного пользователя
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app /venv

USER appuser

ENV PATH="/venv/bin:$PATH"

# Запускаем миграции и приложение
CMD ["sh", "-c", "alembic upgrade head && python main.py"]