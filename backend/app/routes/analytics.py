"""
Analytics and visualization routes.

Endpoints:
    GET /api/plot/expense_distribution  — Bar chart image of expenses
    GET /api/plot/expense_pie_chart     — Pie chart image of expenses
    GET /api/ml/metrics                 — ML model evaluation metrics
"""

import logging
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.extensions import get_db
from app.services.ml_service import get_metrics, train_and_evaluate

logger = logging.getLogger(__name__)

analytics_router = APIRouter()


@analytics_router.get('/plot/expense_distribution')
def plot_expense_distribution(user_id: str):
    """Generate a stacked bar chart of expenses by category (Paid vs Owed)."""
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user ID provided"
            )

        db = get_db()
        expense_sums = list(db[f'{user_id}_expense_sums'].find({}, {'_id': 0}))

        if not expense_sums:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No expense data available'
            )

        plt.figure(figsize=(10, 6))
        categories = [e['predicted_expense_type'] for e in expense_sums]
        paid = [e['Paid Amount'] for e in expense_sums]
        owed = [e['Owed Amount'] for e in expense_sums]

        plt.bar(categories, paid, label='Paid')
        plt.bar(categories, owed, bottom=paid, label='Owed')
        plt.xlabel('Expense Type')
        plt.ylabel('Amount (INR)')
        plt.title('Expense Distribution')
        plt.legend()
        plt.xticks(rotation=45, ha='right')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()

        return StreamingResponse(buf, media_type='image/png')
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating expense distribution: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@analytics_router.get('/plot/expense_pie_chart')
def plot_expense_pie_chart(user_id: str):
    """Generate a pie chart of expense distribution by paid amount."""
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user ID provided"
            )

        db = get_db()
        expense_sums = list(db[f'{user_id}_expense_sums'].find({}, {'_id': 0}))

        if not expense_sums:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No expense data available'
            )

        plt.figure(figsize=(8, 8))
        plt.pie(
            [e['Paid Amount'] for e in expense_sums],
            labels=[e['predicted_expense_type'] for e in expense_sums],
            autopct='%1.1f%%'
        )
        plt.title('Expense Distribution (Paid Amount)')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()

        return StreamingResponse(buf, media_type='image/png')
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating pie chart: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@analytics_router.get('/ml/metrics')
def ml_metrics():
    """
    Return the ML model's evaluation metrics.

    Provides accuracy, F1, precision, recall, per-category breakdown,
    cross-validation scores, and confusion matrix.
    """
    try:
        metrics = get_metrics()
        return metrics
    except Exception as e:
        logger.error("Error fetching ML metrics: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@analytics_router.post('/ml/retrain')
def ml_retrain():
    """Retrain the ML model and return updated metrics."""
    try:
        metrics = train_and_evaluate()
        return {
            'message': 'Model retrained successfully',
            'metrics': metrics
        }
    except Exception as e:
        logger.error("Error retraining model: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
