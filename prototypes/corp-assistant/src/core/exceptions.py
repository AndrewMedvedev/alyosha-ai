

class AppError(Exception):
    pass


class FileDoesNotExistError(AppError):
    """Файл не найден"""
