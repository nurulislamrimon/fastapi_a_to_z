
import platform
import sys
import time

import fastapi
from fastapi import APIRouter, Request
from database.redis import check_redis
from database.session import check_database


app_router = APIRouter()

@app_router.get(
    "/health",
    tags=["Health"],
    summary="System health check",
)
async def health_check(request: Request):
    app = request.app
    uptime_seconds = time.time() - app.state.start_time
    database_healthy = check_database()

    return {
        "status": "healthy",

        "application": {
            "name": app.title,
            "version": app.version,
            "environment": "development",
        },

        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "architecture": platform.machine(),
        },

        "framework": {
            "fastapi": fastapi.__version__,
        },

        "uptime": {
            "seconds": round(uptime_seconds, 2),
        },

        "dependencies": {
            "database": {                
    "status": "healthy" if database_healthy else "unhealthy",
            },
            "redis": {
                "status": "healthy" if check_redis() else "unhealthy",
            },
        },
    }
