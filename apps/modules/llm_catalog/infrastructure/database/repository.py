from typing import TypeVar

from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from modules.shared_kernel.application import Pagination
from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import CatalogRepository
from ...domain import AnyLLM, CommercialLLM, OpenSourceLLM
from .models import BaseLLMModel, CommercialLLMModel, OpenSourceLLMModel, RatingModel

AnyLLMModel = TypeVar("AnyLLMModel", bound=BaseLLMModel | CommercialLLMModel | OpenSourceLLMModel)


class LLMDataMapper(DataMapper[AnyLLM, AnyLLMModel]):
    @classmethod
    def model_to_entity(cls, model: AnyLLMModel) -> AnyLLM:
        values = {
            "id": model.id,
            "slug": model.slug,
            "name": model.name,
            "provider_name": model.provider_name,
            "source_url": str(model.source_url),
            "release_date": model.release_date,
            "description": model.description,
            "size_type": model.size_type,
            "billion_params_count": model.billion_params_count,
            "context_window_tokens": model.context_window_tokens,
            "category": model.category,
            "capabilities": model.capabilities,
            "modality": model.modality,
            "target_domains": model.target_domains,
            "rating": {
                "count_of_usage": model.rating.count_of_usage,
                "stars": model.rating.stars,
            },
            "created_at": model.created_at,
        }
        if isinstance(model, OpenSourceLLMModel):
            values.update({
                "min_system_requirements": model.min_system_requirements,
                "recommended_system_requirements": model.recommended_system_requirements
            })
            return OpenSourceLLM.model_validate(values)
        values.update({"tariff_method": model.tariff_method})
        return CommercialLLM.model_validate(values)

    @classmethod
    def entity_to_model(cls, entity: AnyLLM) -> AnyLLMModel:
        values = {
            "id": entity.id,
            "slug": entity.slug,
            "name": entity.name,
            "provider_name": entity.provider_name,
            "source_url": str(entity.source_url),
            "release_date": entity.release_date,
            "description": entity.description,
            "size_type": entity.size_type,
            "billion_params_count": entity.billion_params_count,
            "context_window_tokens": entity.context_window_tokens,
            "category": entity.category,
            "capabilities": list(entity.capabilities),
            "modality": entity.modality,
            "target_domains": list(entity.target_domains),
            "rating": RatingModel(
                llm_id=entity.id,
                count_of_usage=entity.rating.count_of_usage,
                stars=entity.rating.stars,
            ),
            "created_at": entity.created_at,
        }
        if isinstance(entity, OpenSourceLLM):
            values.update({
                "min_system_requirements": entity.min_system_requirements.model_dump(),
                "recommended_system_requirements": entity.recommended_system_requirements.model_dump(),  # noqa: E501
            })
            return OpenSourceLLMModel(**values)
        values.update({"tariff_method": entity.tariff_method})
        return CommercialLLMModel(**values)


class SQLAlchemyCatalogRepository(SQLAlchemyRepository[AnyLLM, AnyLLMModel], CatalogRepository):
    entity = AnyLLM
    model = BaseLLMModel
    data_mapper = LLMDataMapper

    async def get_most_popular(self, pagination: Pagination) -> list[AnyLLM]:
        try:
            stmt = (
                select(self.model)
                .join(RatingModel, self.model.id == RatingModel.llm_id)
                .options(selectinload(self.model.rating))
                .order_by(desc(RatingModel.count_of_usage))
                .offset(pagination.offset)
                .limit(pagination.limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [
                self.data_mapper.model_to_entity(model) for model in models
            ]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name="LLM",
                entity_id="*",
                details={**pagination.model_dump()},
                original_error=e
            ) from e
