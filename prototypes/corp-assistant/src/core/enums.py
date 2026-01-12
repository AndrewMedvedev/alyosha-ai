from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
