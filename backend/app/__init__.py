from sanic import Sanic
from sanic.response import json
from .config import settings
import os


def create_app():
    app = Sanic("customer_manager")
    
    app.config.update(
        DATABASE_URL=settings.database_url,
        JWT_SECRET=settings.jwt_secret,
        ENVIRONMENT=settings.environment
    )
    
    @app.get("/health")
    async def health_check(request):
        return json({
            "status": "healthy",
            "version": "1.0.0"
        })
    
    return app


app = create_app()
