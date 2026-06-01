"""
BudgetBliss Backend — FastAPI Application Entry Point.

Usage:
    python run.py                  # Runs uvicorn dev server on port 5000
    FASTAPI_ENV=production python run.py  # Runs production mode
"""

import uvicorn
from app.config import settings

if __name__ == '__main__':
    # Run Uvicorn server referencing the app instance in backend/app/__init__.py
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=getattr(settings, "DEBUG", True)
    )
