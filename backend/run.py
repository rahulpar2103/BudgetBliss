"""
BudgetBliss Backend — Application Entry Point.

Usage:
    python run.py                  # Development mode (default)
    FLASK_ENV=production python run.py  # Production mode
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', True))
