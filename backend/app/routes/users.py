"""
User management routes.

Endpoints:
    GET /api/user_info   — Get current user profile
    GET /api/user_stats  — Get aggregate user statistics
"""

import logging
import json
from flask import Blueprint, jsonify, request

from app.services import splitwise_service, expense_service

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)


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


@users_bp.route('/user_info', methods=['GET'])
def get_user_info():
    """Fetch current user's profile from Splitwise."""
    access_token = _extract_access_token_from_header()
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 401

    try:
        user_info = splitwise_service.fetch_user_info(access_token)
        return jsonify(user_info)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid access token format'}), 400
    except Exception as e:
        logger.error("Error getting user info: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@users_bp.route('/user_stats', methods=['GET'])
def get_user_stats():
    """
    Get aggregate statistics for the authenticated user.

    Returns total expenses count, total amount, groups count,
    friends count, and top spending category.
    """
    access_token = _extract_access_token_from_header()
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 401

    try:
        user_info = splitwise_service.fetch_user_info(access_token)
        stats = expense_service.get_user_stats(user_info['id'])
        return jsonify(stats)
    except Exception as e:
        logger.error("Error getting user stats: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500
