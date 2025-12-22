from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    DateTimeNull,
    JsonFieldNull,
    StrArray,
    StrNull,
    StrText,
)


class BaseLLMModel(Base):
    __tablename__ = "llms"
    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_on": "category",
        "polymorphic_identity": "base",
        "with_polymorphic": "*",
    }

    slug: Mapped[str]
    name: Mapped[str]
    provider_name: Mapped[str]
    source_url: Mapped[str]
    release_date: Mapped[DateTimeNull]
    description: Mapped[StrText]
    size_type: Mapped[str]
    billion_params_count: Mapped[int]
    context_window_tokens: Mapped[int]
    category: Mapped[str]
    capabilities: Mapped[StrArray]
    modality: Mapped[str]
    target_domains: Mapped[StrArray]
    rating: Mapped["RatingModel"] = relationship(
        back_populates="llm", cascade="all, delete-orphan", lazy="selectin"
    )


class RatingModel(Base):
    __tablename__ = "llm_ratings"

    llm_id: Mapped[UUID] = mapped_column(ForeignKey("llms.id"), unique=True)
    count_of_usage: Mapped[int]
    stars: Mapped[int]

    llm: Mapped["BaseLLMModel"] = relationship(back_populates="rating")


class OpenSourceLLMModel(BaseLLMModel):
    __mapper_args__ = {"polymorphic_identity": "open-source"}  # noqa: RUF012

    min_system_requirements: Mapped[JsonFieldNull]
    recommended_system_requirements: Mapped[JsonFieldNull]


class CommercialLLMModel(BaseLLMModel):
    __mapper_args__ = {"polymorphic_identity": "commercial"}  # noqa: RUF012

    tariff_method: Mapped[StrNull]
