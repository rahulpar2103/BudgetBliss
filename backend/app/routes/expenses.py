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
from flask import Blueprint, jsonify, request

from app.services import splitwise_service, expense_service
from app.services.ml_service import process_expenses as ml_process_expenses

logger = logging.getLogger(__name__)

expenses_bp = Blueprint('expenses', __name__)


def _extract_access_token_from_header():
    """Extract and parse the access token from the Authorization header."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    token_str = auth_header.split(' ', 1)[1] if ' ' in auth_header else auth_header
    try:
        return json.loads(token_str)
    except json.JSONDecodeError:
        return None


@expenses_bp.route('/fetch_data', methods=['POST'])
def fetch_data():
    """Sync user data (friends, groups, expenses) from Splitwise."""
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'No access token provided'}), 400

        summary = splitwise_service.fetch_user_data(access_token)
        return jsonify({
            'message': 'Data fetched successfully',
            'summary': summary
        })
    except Exception as e:
        logger.error("Error fetching data: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@expenses_bp.route('/process_expenses', methods=['POST'])
def process_expenses_route():
    """Run ML categorization pipeline on user's expenses."""
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'No access token provided'}), 400

        # Get user ID
        user_info = splitwise_service.fetch_user_info(access_token)
        user_id = user_info['id']

        from flask import current_app
        result = ml_process_expenses(user_id, app_config=current_app.config)
        return jsonify({
            'message': 'Expenses processed successfully',
            'result': result
        })
    except Exception as e:
        logger.error("Error processing expenses: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@expenses_bp.route('/get_results', methods=['GET'])
def get_results():
    """Retrieve categorized expense predictions and summaries."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400

        results = expense_service.get_user_results(user_id)
        return jsonify({
            'predictions': json.dumps(results['predictions'], default=str),
            'expense_sums': json.dumps(results['expense_sums'], default=str)
        })
    except Exception as e:
        logger.error("Error getting results: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@expenses_bp.route('/add_expense', methods=['POST'])
def add_expense():
    """Manually add a new expense entry."""
    access_token = _extract_access_token_from_header()
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 401

    try:
        user_info = splitwise_service.fetch_user_info(access_token)
        user_id = user_info['id']

        expense_data = request.json
        expense_service.add_expense(
            user_id=user_id,
            description=expense_data['description'],
            amount=expense_data['amount'],
            category=expense_data['category']
        )

        # Re-process expenses to update predictions
        from flask import current_app
        ml_process_expenses(user_id, app_config=current_app.config)

        return jsonify({'message': 'Expense added successfully'}), 200
    except Exception as e:
        logger.error("Error adding expense: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500
