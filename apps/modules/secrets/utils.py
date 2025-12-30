from typing import Final

import base64
import logging
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.dev import settings

from .domain.exceptions import DecryptionError

logger = logging.getLogger(__name__)


class StringEncryptor:
    """Шифрование и дешифрование строк используя AES - алгоритмы"""

    TAG_LENGTH = 16

    def __init__(
            self,
            encryption_key: str,
            key_length: int,
            iterations: int = 100_000,
    ) -> None:
        """
        :param encryption_key: Ключ шифрования. Если None, будет использован из env.
        :param key_length: Длина ключа в байтах (32 для AES-256).
        :param iterations: Количество итераций для PBKDF2.
        """

        self._encryption_key = encryption_key.encode("utf-8")
        self._key_length = key_length
        self._iterations = iterations

    @staticmethod
    def _generate_salt() -> bytes:
        """Генерация случайной соли"""

        return secrets.token_bytes(16)

    def _ensure_aes_key_length(self, key: bytes) -> bytes:
        """Обеспечение правильной длины ключа для AES"""

        if len(key) == self._key_length:
            return key
        return (
            key.ljust(32, b"\x00")
            if len(key) < self._key_length
            else key[:self._key_length]
        )

    def _derive_key(self, salt: bytes) -> bytes:
        """Деривация ключа (KDF, Key Derivation Function)"""

        kbf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self._key_length,
            salt=salt,
            iterations=self._iterations,
            backend=default_backend()
        )
        return kbf.derive(self._encryption_key)

    def encrypt(self, string: str, context: str | None = None) -> str:
        """Шифрование строки с использованием AES-GCM.

        :param string: Строка, которую нужно зашифровать.
        :param context: Контекстная информация для зашиты от подмены.
        :returns: Зашифрованная строка в формате: base64(salt + nonce + ciphertext + tag)
        """

        string_to_encrypt = string if context is None else f"{context}:{string}"
        string_to_encrypt = string_to_encrypt.encode("utf-8")
        salt = self._generate_salt()
        nonce = secrets.token_bytes(12)
        derived_key = self._derive_key(salt)
        aes_key = self._ensure_aes_key_length(derived_key)
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        # Шифрование строки
        ciphertext = encryptor.update(string_to_encrypt) + encryptor.finalize()
        tag = encryptor.tag
        # Объединение компонентов: salt (16) + nonce (12) + ciphertext + tag (16)
        combined = salt + nonce + ciphertext + tag
        # Кодировка в base64 для удобного хранения
        return base64.urlsafe_b64encode(combined).decode("utf-8")

    def decrypt(
            self, encrypted_string: str, expected_context: str | None = None,
    ) -> str:
        """Дешифрование строки.

        :param encrypted_string: Зашифрованная строка в формате (salt + nonce + ciphertext + tag)
        :param expected_context: Ожидаемый контекст для проверки.
        :returns: Расшифрованная строка.
        """

        try:
            combined = base64.urlsafe_b64decode(encrypted_string)
            # Извлечение компонентов (фиксированные размеры для salt и nonce)
            salt = combined[:16]  # salt всегда 16 байт
            nonce = combined[16:28]  # nonce всегда 12 байт
            # Остальное: ciphertext + tag (tag всегда 16 байт)
            ciphertext_and_tag = combined[28:]
            # Отделяем tag от ciphertext
            ciphertext = ciphertext_and_tag[:-self.TAG_LENGTH]
            tag = ciphertext_and_tag[-self.TAG_LENGTH:]
            # Деривация ключа
            derived_key = self._derive_key(salt)
            aes_key = self._ensure_aes_key_length(derived_key)
            # Создание cipher для AES-GCM
            cipher = Cipher(
                algorithms.AES(aes_key), modes.GCM(nonce, tag), backend=default_backend()
            )
            decryptor = cipher.decryptor()
            # Дешифрование
            decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            decrypted_text = decrypted_bytes.decode("utf-8")
            if expected_context is not None:
                if ":" not in decrypted_text:
                    raise DecryptionError("No context separator found in decrypted text")
                context, plaintext = decrypted_text.split(":", maxsplit=1)
                if context != expected_context:
                    raise DecryptionError(
                        f"Context mismatch. Expected: {expected_context}, got: {context}"
                    )
                return plaintext
        except InvalidTag as e:
            logger.critical("Decryption failed: Invalid authentication tag", exc_info=True)
            raise DecryptionError(
                "Authentication failed - data may have been tampered with"
            ) from e
        else:
            return decrypted_text


string_encryptor: Final[StringEncryptor] = StringEncryptor(
    encryption_key=settings.encryption.key,
    key_length=settings.encryption.key_length,
    iterations=settings.encryption.iterations,
)
