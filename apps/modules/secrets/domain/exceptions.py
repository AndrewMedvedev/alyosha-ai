from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class DecryptionError(AppError):
    """Ошибка дешифрования"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.VALIDATION_ERROR,
            code="DECRYPTION_FAILED",
            details=details
        )
