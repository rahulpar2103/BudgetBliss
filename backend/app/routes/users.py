"""
User management routes.

Endpoints:
    GET /api/user_info   — Get current user profile
    GET /api/user_stats  — Get aggregate user statistics
"""

import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status

from app.services import splitwise_service, expense_service
from app.routes.expenses import extract_access_token

logger = logging.getLogger(__name__)

users_router = APIRouter()


@users_router.get('/user_info')
def get_user_info(authorization: Optional[str] = Header(None)):
    """Fetch current user's profile from Splitwise."""
    token = extract_access_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided"
        )

    try:
        user_info = splitwise_service.fetch_user_info(token)
        return user_info
    except Exception as e:
        logger.error("Error getting user info: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@users_router.get('/user_stats')
def get_user_stats(authorization: Optional[str] = Header(None)):
    """
    Get aggregate statistics for the authenticated user.

    Returns total expenses count, total amount, groups count,
    friends count, and top spending category.
    """
    token = extract_access_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided"
        )

    try:
        user_info = splitwise_service.fetch_user_info(token)
        stats = expense_service.get_user_stats(user_info['id'])
        return stats
    except Exception as e:
        logger.error("Error getting user stats: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
