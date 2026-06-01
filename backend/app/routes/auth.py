"""
Authentication routes — Splitwise OAuth flow.

Endpoints:
    POST /api/authorize  — Initiate OAuth, returns authorization URL
    POST /api/callback   — Exchange OAuth tokens for access token
"""

import logging
from flask import Blueprint, jsonify, request

from app.services import splitwise_service

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/authorize', methods=['POST'])
def authorize():
    """Generate a Splitwise OAuth authorization URL."""
    try:
        url, secret = splitwise_service.get_authorize_url()
        return jsonify({'url': url, 'secret': secret})
    except Exception as e:
        logger.error("Authorization failed: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/callback', methods=['POST'])
def callback():
    """Exchange OAuth credentials for an access token."""
    data = request.json
    logger.debug("Received callback data: %s", data)

    oauth_token = data.get('oauth_token')
    oauth_verifier = data.get('oauth_verifier')
    secret = data.get('secret')

    if not all([oauth_token, oauth_verifier, secret]):
        return jsonify({'error': 'Missing required parameters (oauth_token, oauth_verifier, secret)'}), 400

    try:
        access_token = splitwise_service.get_access_token(oauth_token, secret, oauth_verifier)
        return jsonify({'access_token': access_token})
    except Exception as e:
        logger.error("Callback token exchange failed: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500
