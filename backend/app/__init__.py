"""
BudgetBliss Flask Application Factory.

Implements the application factory pattern for clean initialization,
Blueprint registration, and environment-specific configuration.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import config_by_name
from app.extensions import init_db
from app.utils.logging_config import setup_logging


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration environment ('development', 'production', 'testing').
                     Defaults to FLASK_ENV environment variable or 'development'.

    Returns:
        Configured Flask application instance.
    """
    import os
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize logging
    setup_logging(app.config.get('LOG_LEVEL', 'INFO'))

    # Initialize extensions
    CORS(app)
    init_db(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    logger = logging.getLogger(__name__)
    logger.info(
        "BudgetBliss app created with '%s' configuration", config_name
    )

    return app


def _register_blueprints(app):
    """Register all route Blueprints with the application."""
    from app.routes.auth import auth_bp
    from app.routes.expenses import expenses_bp
    from app.routes.analytics import analytics_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(expenses_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')


def _register_error_handlers(app):
    """Register global error handlers for consistent API responses."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger = logging.getLogger(__name__)
        logger.error("Internal server error: %s", str(error), exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
