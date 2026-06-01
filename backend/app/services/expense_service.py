"""
Expense processing service.

Handles expense CRUD operations and data retrieval from MongoDB.
Extracted from the original api.py route handlers.
"""

import logging
import uuid
from datetime import datetime

from bson.decimal128 import Decimal128

from app.extensions import get_db

logger = logging.getLogger(__name__)


def get_user_results(user_id):
    """
    Retrieve processed predictions and expense summaries for a user.

    Args:
        user_id: The Splitwise user ID.

    Returns:
        dict: {'predictions': [...], 'expense_sums': [...]} or None.
    """
    db = get_db()

    predictions = list(db[f'{user_id}_predictions'].find({}, {'_id': 0}))
    expense_sums = list(db[f'{user_id}_expense_sums'].find({}, {'_id': 0}))

    logger.info(
        "Retrieved results for user %s: %d predictions, %d category sums",
        user_id, len(predictions), len(expense_sums)
    )

    return {
        'predictions': predictions,
        'expense_sums': expense_sums
    }


def add_expense(user_id, description, amount, category):
    """
    Add a manual expense entry for a user.

    Args:
        user_id: The Splitwise user ID.
        description: Expense description text.
        amount: Expense amount (numeric).
        category: Expense category label.

    Returns:
        dict: The created expense document.
    """
    db = get_db()

    new_expense = {
        'id': str(uuid.uuid4()),
        'Description': description,
        'Cost': Decimal128(str(amount)),
        'Currency Code': 'INR',
        'Date': datetime.now().isoformat(),
        'Created By': 'User',
        'expense_type': category,
        'deleted_at': None
    }

    db[f'{user_id}_expenses'].insert_one(new_expense)

    logger.info(
        "Added expense for user %s: '%s' — ₹%s [%s]",
        user_id, description, amount, category
    )

    return new_expense


def get_user_stats(user_id):
    """
    Compute aggregate statistics for a user's expenses.

    Used to populate the Profile page with real data instead of placeholders.

    Args:
        user_id: The Splitwise user ID.

    Returns:
        dict: {total_expenses, total_amount, groups_count, friends_count, top_category}
    """
    db = get_db()

    # Count expenses
    expenses = list(db[f'{user_id}_expenses'].find({}, {'_id': 0}))
    expense_count = len(expenses)

    # Sum total cost
    total_amount = 0.0
    for exp in expenses:
        cost = exp.get('total_cost') or exp.get('Cost', 0)
        try:
            if isinstance(cost, Decimal128):
                total_amount += float(cost.to_decimal())
            else:
                total_amount += float(cost)
        except (TypeError, ValueError):
            pass

    # Count groups and friends
    groups_count = db[f'{user_id}_groups'].count_documents({})
    friends_count = db[f'{user_id}_friends'].count_documents({})

    # Find top category from expense sums
    expense_sums = list(db[f'{user_id}_expense_sums'].find({}, {'_id': 0}))
    top_category = 'N/A'
    if expense_sums:
        top = max(expense_sums, key=lambda x: x.get('Paid Amount', 0))
        top_category = top.get('predicted_expense_type', 'N/A')

    stats = {
        'total_expenses': expense_count,
        'total_amount': round(total_amount, 2),
        'groups_count': groups_count,
        'friends_count': friends_count,
        'top_category': top_category
    }

    logger.info("Computed stats for user %s: %s", user_id, stats)
    return stats
