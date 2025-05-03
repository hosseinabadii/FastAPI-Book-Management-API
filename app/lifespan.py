from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.config import Config
from app.db.main import init_db

if Config.USE_REDIS:
    from app.db.redis_client import init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running lifespan before the application startup!")
    await init_db()
    if Config.USE_REDIS:
        await init_redis()
    yield
    logger.info("Running lifespan after the application shutdown!")
