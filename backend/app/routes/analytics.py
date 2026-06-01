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
from flask import Blueprint, jsonify, request, send_file

from app.extensions import get_db
from app.services.ml_service import get_metrics, train_and_evaluate

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/plot/expense_distribution', methods=['GET'])
def plot_expense_distribution():
    """Generate a stacked bar chart of expenses by category (Paid vs Owed)."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400

        db = get_db()
        expense_sums = list(db[f'{user_id}_expense_sums'].find({}, {'_id': 0}))

        if not expense_sums:
            return jsonify({'error': 'No expense data available'}), 404

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

        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.error("Error generating expense distribution: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/plot/expense_pie_chart', methods=['GET'])
def plot_expense_pie_chart():
    """Generate a pie chart of expense distribution by paid amount."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400

        db = get_db()
        expense_sums = list(db[f'{user_id}_expense_sums'].find({}, {'_id': 0}))

        if not expense_sums:
            return jsonify({'error': 'No expense data available'}), 404

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

        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.error("Error generating pie chart: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/ml/metrics', methods=['GET'])
def ml_metrics():
    """
    Return the ML model's evaluation metrics.

    Provides accuracy, F1, precision, recall, per-category breakdown,
    cross-validation scores, and confusion matrix.
    """
    try:
        from flask import current_app
        metrics = get_metrics(app_config=current_app.config)
        return jsonify(metrics)
    except Exception as e:
        logger.error("Error fetching ML metrics: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/ml/retrain', methods=['POST'])
def ml_retrain():
    """Retrain the ML model and return updated metrics."""
    try:
        from flask import current_app
        metrics = train_and_evaluate(app_config=current_app.config)
        return jsonify({
            'message': 'Model retrained successfully',
            'metrics': metrics
        })
    except Exception as e:
        logger.error("Error retraining model: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500
