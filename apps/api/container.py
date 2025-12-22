from typing import Final

from dishka import AsyncContainer, make_async_container

from modules.iam.infrastructure.container import IAMProvider
from modules.llm_catalog.infrastructure.container import LLMCatalogProvider
from modules.shared_kernel.insrastructure.container import SharedKernelProvider
from modules.workspaces.infrastructure.container import WorkspaceProvider

container: Final[AsyncContainer] = make_async_container(
    SharedKernelProvider(), IAMProvider(), LLMCatalogProvider(), WorkspaceProvider(),
)
