from modules.secrets.utils import string_encryptor

apikey = "1234567890"

print(f"Исходный ключ: {apikey}")

encrypted_apikey = string_encryptor.encrypt(apikey, context="hello")

print(f"Зашифрованный ключ: {encrypted_apikey}")

decrypted_apikey = string_encryptor.decrypt(
    encrypted_apikey, expected_context="hello"
)

print(f"Расшифрованный ключ: {decrypted_apikey}")
