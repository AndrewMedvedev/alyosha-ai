__all__ = ("router",)

from fastapi import APIRouter

from .auth import router as auth_router
from .chat import router as chat_router
from .files import router as files_router
from .llms_catalog import router as models_registry_router
from .users import router as users_router
from .workspace import router as workspaces_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(users_router)
router.include_router(files_router)
router.include_router(workspaces_router)
router.include_router(models_registry_router)
