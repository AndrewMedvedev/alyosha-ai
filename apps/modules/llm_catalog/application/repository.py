from abc import abstractmethod

from modules.shared_kernel.application import CRUDRepository, Pagination

from ..domain import AnyLLM


class CatalogRepository(CRUDRepository[AnyLLM]):
    @abstractmethod
    async def get_most_popular(self, pagination: Pagination) -> list[...]: ...
