"""
Pydantic data schemas for request validation in BudgetBliss.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any


class CallbackPayload(BaseModel):
    oauth_token: str = Field(..., description="The OAuth token returned by Splitwise")
    oauth_verifier: str = Field(..., description="The OAuth verifier returned by Splitwise")
    secret: str = Field(..., description="The temporary OAuth secret from authorization step")


class FetchDataPayload(BaseModel):
    access_token: Dict[str, Any] = Field(..., description="OAuth access token dictionary")


class ProcessExpensesPayload(BaseModel):
    access_token: Dict[str, Any] = Field(..., description="OAuth access token dictionary")


class AddExpensePayload(BaseModel):
    description: str = Field(..., min_length=1, description="Expense description text")
    amount: float = Field(..., gt=0, description="Expense cost amount, must be greater than zero")
    category: str = Field(..., min_length=1, description="Assigned category for the expense")
