"""
Shared helper functions for BudgetBliss.
"""

from decimal import Decimal
from bson.decimal128 import Decimal128


def format_inr(amount):
    """
    Format a numeric amount as Indian Rupee currency string.

    Args:
        amount: Numeric value to format.

    Returns:
        Formatted string like '₹1,234.56' or 'N/A' for invalid values.
    """
    try:
        return f"₹{float(amount):,.2f}"
    except (TypeError, ValueError):
        return 'N/A'


def decimal128_to_float(value):
    """
    Safely convert a BSON Decimal128 or any numeric type to float.

    Args:
        value: A Decimal128, Decimal, int, float, str, or None.

    Returns:
        Float representation of the value, or 0.0 for None/invalid.
    """
    if value is None:
        return 0.0
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
