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


def init_db(config=None):
    """
    Initialize the MongoDB connection using configuration.

    Stores the client and database reference at module level for access via get_db().
    """
    global _mongo_client, _db

    from app.config import settings
    active_config = config or settings

    mongo_uri = getattr(active_config, 'MONGODB_URI', 'mongodb://localhost:27017')
    db_name = getattr(active_config, 'MONGODB_DB_NAME', 'budget_bliss')

    _mongo_client = MongoClient(mongo_uri)
    _db = _mongo_client[db_name]

    logger.info("MongoDB connected: %s / %s", mongo_uri, db_name)


def get_db():
    """
    Get the MongoDB database instance. Auto-connects if not yet initialized.

    Returns:
        pymongo.database.Database: The configured database.
    """
    global _db
    if _db is None:
        init_db()
    return _db
