from fastapi import APIRouter

# internal imports
from modules.app import app_router
from modules.auth.router import router as auth_router

router = APIRouter()

router.include_router(app_router)
router.include_router(auth_router)