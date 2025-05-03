import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_sqlalchemy_monitor import AlchemyStatistics, SQLAlchemyMonitor
from fastapi_sqlalchemy_monitor.action import Action

from app.config import Config
from app.db.main import engine

# You can disable the uvicorn logger
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.disabled = False


class CustomPrintStatistics(Action):
    """Action that prints current statistics."""

    def handle(self, statistics: AlchemyStatistics):
        print("-" * 50)
        print(str(statistics))
        query_stats = statistics.query_stats
        for index, query_stat in enumerate(query_stats.values(), start=1):
            print("-" * 50)
            print(f"Query {index}")
            print(query_stat.query)
        print("-" * 50)


def register_middleware(app: FastAPI):
    if Config.USE_SQLAlCHEMY_MONITOR:
        app.add_middleware(
            SQLAlchemyMonitor,
            engine=engine,
            actions=[CustomPrintStatistics()],
            allow_no_request_context=True,
        )

    @app.middleware("http")
    async def custom_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:0.4f}s"
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "test"],
    )
