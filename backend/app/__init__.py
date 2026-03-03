import os

from sanic import Sanic
from sanic.response import json

from .config import settings
from .database import Base, engine
from .middlewares.auth import attach_auth_middleware, require_auth_middleware


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app():
    app = Sanic("customer_manager")

    app.config.update(
        DATABASE_URL=settings.database_url,
        JWT_SECRET=settings.jwt_secret,
        ENVIRONMENTIRONMENT=settings.environment,
    )

    attach_auth_middleware(app)
    require_auth_middleware(app)

    @app.get("/health")
    async def health_check(request):
        return json({"status": "healthy", "version": "1.0.0"})

    @app.listener("before_server_start")
    async def setup_database(app):
        await init_db()

    return app


app = create_app()
