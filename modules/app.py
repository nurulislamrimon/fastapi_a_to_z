
from fastapi import APIRouter

app_router = APIRouter()

app_router.get(
    "/health",
    tags=["Health"],
    summary="System health check",
)
async def health_check():
    uptime_seconds = time.time() - app.state.start_time

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
                "status": "not_configured",
            },
            "redis": {
                "status": "not_configured",
            },
        },
    }