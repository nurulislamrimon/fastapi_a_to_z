import time
from contextlib import asynccontextmanager
from typing import  AsyncIterator

from fastapi import FastAPI

# internal imports
from routes.router import router


START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifecycle.

    Startup code goes before `yield`.
    Shutdown/cleanup code goes after `yield`.
    """

    app.state.start_time = time.time()

    print("Application starting...")

    yield

    print("Application shutting down...")


app = FastAPI(
    title="CRUD API",
    description="Production-ready CRUD API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.include_router(
    router=router,
    prefix="/api",
    tags=["API"],
)
