"""
Application factory for the FastAPI application.
"""
from fastapi import FastAPI
from src.api.routes import users
from src.api import metrics


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Prima API",
        description="User management service with avatar upload capabilities",
        docs_url="/docs",
        openapi_url="/openapi.json",
        version="1.0.0"
    )
    
    # Include routers
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(metrics.router)
    
    return app