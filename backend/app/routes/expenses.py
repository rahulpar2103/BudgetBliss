"""
Expense management routes.

Endpoints:
    POST /api/fetch_data        — Sync expenses from Splitwise
    POST /api/process_expenses  — Run ML categorization on user expenses
    GET  /api/get_results       — Retrieve categorized results
    POST /api/add_expense       — Manually add an expense
"""

import logging
import json
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status, Depends

from app.services import splitwise_service, expense_service
from app.services.ml_service import process_expenses as ml_process_expenses
from app.schemas import FetchDataPayload, ProcessExpensesPayload, AddExpensePayload

logger = logging.getLogger(__name__)

expenses_router = APIRouter()


def extract_access_token(authorization: Optional[str]) -> Optional[dict]:
    """Extract and parse the access token from the Authorization header."""
    if not authorization:
        return None

    try:
        # Standard Bearer token handling
        if authorization.startswith('Bearer '):
            token_str = authorization[7:]
        else:
            token_str = authorization
        return json.loads(token_str)
    except Exception:
        return None


@expenses_router.post('/fetch_data')
def fetch_data(payload: FetchDataPayload):
    """Sync user data (friends, groups, expenses) from Splitwise."""
    try:
        summary = splitwise_service.fetch_user_data(payload.access_token)
        return {
            'message': 'Data fetched successfully',
            'summary': summary
        }
    except Exception as e:
        logger.error("Error fetching data: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@expenses_router.post('/process_expenses')
def process_expenses_route(payload: ProcessExpensesPayload):
    """Run ML categorization pipeline on user's expenses."""
    try:
        # Get user ID
        user_info = splitwise_service.fetch_user_info(payload.access_token)
        user_id = user_info['id']

        result = ml_process_expenses(user_id)
        return {
            'message': 'Expenses processed successfully',
            'result': result
        }
    except Exception as e:
        logger.error("Error processing expenses: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@expenses_router.get('/get_results')
def get_results(
    user_id: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """Retrieve categorized expense predictions and summaries."""
    try:
        resolved_user_id = user_id

        # Fallback to authorization header if query param is not provided
        if not resolved_user_id:
            token = extract_access_token(authorization)
            if token:
                try:
                    user_info = splitwise_service.fetch_user_info(token)
                    resolved_user_id = user_info['id']
                except Exception:
                    pass

        if not resolved_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user ID provided"
            )

        results = expense_service.get_user_results(resolved_user_id)
        return {
            'predictions': json.dumps(results['predictions'], default=str),
            'expense_sums': json.dumps(results['expense_sums'], default=str)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting results: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@expenses_router.post('/add_expense')
def add_expense(
    payload: AddExpensePayload,
    authorization: Optional[str] = Header(None)
):
    """Manually add a new expense entry."""
    token = extract_access_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided"
        )

    try:
        user_info = splitwise_service.fetch_user_info(token)
        user_id = user_info['id']

        expense_service.add_expense(
            user_id=user_id,
            description=payload.description,
            amount=payload.amount,
            category=payload.category
        )

        # Re-process expenses to update predictions
        ml_process_expenses(user_id)

        return {'message': 'Expense added successfully'}
    except Exception as e:
        logger.error("Error adding expense: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
