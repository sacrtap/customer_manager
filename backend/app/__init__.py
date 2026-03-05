import os

from sanic import Sanic
from sanic.response import json

from .config import settings
from .database import Base, engine
from .middlewares.auth import attach_auth_middleware, require_auth_middleware
from .blueprints import (
    customer,
    auth,
    role,
    system,
    pricing_strategy,
    price_config,
    price_band,
    health,
    billing,
    user,
    transfer,
)


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app():
    app = Sanic("customer_manager")

    app.config.update(
        DATABASE_URL=settings.database_url,
        JWT_SECRET=settings.jwt_secret,
        ENVIRONMENTATION=settings.environment,
    )

    attach_auth_middleware(app)
    require_auth_middleware(app)

    app.blueprint(auth.auth_bp)
    app.blueprint(customer.customer_bp)
    app.blueprint(role.role_bp)
    app.blueprint(system.system_bp)
    app.blueprint(user.user_bp)
    app.blueprint(pricing_strategy.pricing_strategy_bp)
    app.blueprint(price_config.price_config_bp)
    app.blueprint(price_band.price_band_bp)
    app.blueprint(health.health_bp)
    app.blueprint(billing.billing_bp)
    app.blueprint(transfer.transfer_bp)

    @app.get("/health")
    async def health_check(request):
        return json({"status": "healthy", "version": "1.0.0"})

    @app.listener("before_server_start")
    async def setup_database(app):
        await init_db()

    return app


app = create_app()
