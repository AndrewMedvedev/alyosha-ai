from sqlalchemy import LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped

from modules.shared_kernel.insrastructure.database import Base, JsonField, UUIDField


class SecretModel(Base):
    __tablename__ = "secrets"

    user_id: Mapped[UUIDField]
    name: Mapped[str]
    description: Mapped[str]
    secret_type: Mapped[str]
    encrypted_data: Mapped[LargeBinary]
    encryption_context: Mapped[JsonField]

    __table_args__ = (UniqueConstraint("user_id", "name", name="user_secret_uq"),)
