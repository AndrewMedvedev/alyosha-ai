from abc import abstractmethod

from modules.shared_kernel.application import CRUDRepository, Pagination

from ..domain import ModelEntry


class RegistryRepository(CRUDRepository[ModelEntry]):
    @abstractmethod
    async def get_most_popular(self, pagination: Pagination) -> list[ModelEntry]: ...
