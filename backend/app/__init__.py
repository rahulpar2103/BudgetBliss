"""
BudgetBliss FastAPI Application Setup.

Implements application initialization, router registration,
CORS middleware configuration, and logging setup.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.extensions import init_db
from app.utils.logging_config import setup_logging


def create_app():
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI application instance.
    """
    # Initialize logging
    setup_logging(settings.LOG_LEVEL)

    # Initialize database connection
    init_db(settings)

    # Create FastAPI app
    app = FastAPI(
        title="BudgetBliss API",
        description="FastAPI Backend for BudgetBliss expense tracker",
        version="1.0.0"
    )

    # Configure CORS middleware (matching Flask CORS defaults)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    _register_routers(app)

    logger = logging.getLogger(__name__)
    logger.info(
        "BudgetBliss FastAPI app created with settings env_name='%s'",
        settings.__class__.__name__
    )

    return app


def _register_routers(app: FastAPI):
    """Register all APIRouters with the application."""
    from app.routes.auth import auth_router
    from app.routes.expenses import expenses_router
    from app.routes.analytics import analytics_router
    from app.routes.users import users_router

    # Mount routers under /api prefix to match existing frontend endpoint expectations
    app.include_router(auth_router, prefix="/api")
    app.include_router(expenses_router, prefix="/api")
    app.include_router(analytics_router, prefix="/api")
    app.include_router(users_router, prefix="/api")


# Instantiate the app for ASGI server (e.g. Uvicorn) import
app = create_app()
