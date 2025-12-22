from typing import ClassVar

import re

from modules.shared_kernel.domain import StrPrimitive


class ModelSlug(StrPrimitive):
    """Идентификатор модели, например `deepseek-ai/DeepSeek-V3`"""

    # Регулярное выражение для валидации slug
    # Разрешает: буквы, цифры, дефисы, точки, нижние подчеркивания
    # Формат: provider/model-name или provider/model-name-version
    SLUG_PATTERN: ClassVar[str] = r"^[a-zA-Z0-9][a-zA-Z0-9_-]*/[a-zA-Z0-9][a-zA-Z0-9._-]*$"
    MAX_SLUG_LENGTH = 255
    MIN_SLUG_PARTS = 2

    @classmethod
    def validate(cls, slug: str) -> str:
        slug = slug.strip()
        if len(slug) > cls.MAX_SLUG_LENGTH:
            raise ValueError(f"Model slug too long (max 255 chars): {slug}")
        if "/" not in slug:
            raise ValueError(f"Model slug must contain '/' (e.g., 'google/gemma-7b'): {slug}")
        parts = slug.split("/")
        if len(parts) != cls.MIN_SLUG_PARTS:
            raise ValueError(f"Model slug must have exactly one '/': {slug}")
        if not re.match(cls.SLUG_PATTERN, slug):
            raise ValueError(
                f"Invalid model slug format. Must match: {cls.SLUG_PATTERN}. Got: {slug}"
            )
        return slug
