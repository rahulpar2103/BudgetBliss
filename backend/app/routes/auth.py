"""
Authentication routes — Splitwise OAuth flow.

Endpoints:
    POST /api/authorize  — Initiate OAuth, returns authorization URL
    POST /api/callback   — Exchange OAuth tokens for access token
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.services import splitwise_service
from app.schemas import CallbackPayload

logger = logging.getLogger(__name__)

auth_router = APIRouter()


@auth_router.post('/authorize')
def authorize():
    """Generate a Splitwise OAuth authorization URL."""
    try:
        url, secret = splitwise_service.get_authorize_url()
        return {'url': url, 'secret': secret}
    except Exception as e:
        logger.error("Authorization failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@auth_router.post('/callback')
def callback(payload: CallbackPayload):
    """Exchange OAuth credentials for an access token."""
    try:
        access_token = splitwise_service.get_access_token(
            payload.oauth_token, payload.secret, payload.oauth_verifier
        )
        return {'access_token': access_token}
    except Exception as e:
        logger.error("Callback token exchange failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
