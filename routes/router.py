from fastapi import APIRouter

# internal imports
from modules.app import app_router

router = APIRouter()

router.include_router(app_router)