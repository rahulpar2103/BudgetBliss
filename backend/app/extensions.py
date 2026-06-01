"""
Extension initialization for BudgetBliss.

Centralizes MongoDB client creation so all modules share a single
connection pool instead of each file creating its own MongoClient.
"""

import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)

# Module-level references — set during app initialization
_mongo_client = None
_db = None


def init_db(app):
    """
    Initialize the MongoDB connection using app configuration.

    Called once during app factory creation. Stores the client and
    database reference at module level for access via get_db().
    """
    global _mongo_client, _db

    mongo_uri = app.config.get('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = app.config.get('MONGODB_DB_NAME', 'budget_bliss')

    _mongo_client = MongoClient(mongo_uri)
    _db = _mongo_client[db_name]

    logger.info("MongoDB connected: %s / %s", mongo_uri, db_name)


def get_db():
    """
    Get the MongoDB database instance.

    Returns:
        pymongo.database.Database: The configured database.

    Raises:
        RuntimeError: If called before init_db().
    """
    if _db is None:
        raise RuntimeError(
            "Database not initialized. Call init_db(app) first."
        )
    return _db
