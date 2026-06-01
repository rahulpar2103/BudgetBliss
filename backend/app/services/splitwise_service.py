"""
Splitwise API interaction service.

Encapsulates all Splitwise SDK calls — authentication, data fetching,
and user operations. Extracted from the original main.py.
"""

import logging
from flask import current_app
from splitwise import Splitwise

from app.extensions import get_db

logger = logging.getLogger(__name__)


def get_splitwise_instance():
    """Create a Splitwise SDK instance using app configuration."""
    return Splitwise(
        current_app.config['SPLITWISE_CONSUMER_KEY'],
        current_app.config['SPLITWISE_CONSUMER_SECRET']
    )


def get_authorize_url():
    """
    Generate a Splitwise OAuth authorization URL.

    Returns:
        tuple: (authorize_url, oauth_secret)
    """
    sObj = get_splitwise_instance()
    url, secret = sObj.getAuthorizeURL()
    logger.info("Generated Splitwise authorization URL")
    return url, secret


def get_access_token(oauth_token, secret, oauth_verifier):
    """
    Exchange OAuth credentials for an access token.

    Args:
        oauth_token: Token from callback URL.
        secret: Secret from authorization step.
        oauth_verifier: Verifier from callback URL.

    Returns:
        dict: Access token dictionary.
    """
    sObj = get_splitwise_instance()
    access_token = sObj.getAccessToken(oauth_token, secret, oauth_verifier)
    logger.info("Successfully obtained access token")
    return access_token


def get_authenticated_client(access_token):
    """
    Create an authenticated Splitwise client.

    Args:
        access_token: User's access token (dict).

    Returns:
        Splitwise: Authenticated Splitwise instance.
    """
    sObj = get_splitwise_instance()
    sObj.setAccessToken(access_token)
    return sObj


def fetch_user_info(access_token):
    """
    Fetch current user's profile information.

    Args:
        access_token: User's access token.

    Returns:
        dict: User info with id, name, email, picture.
    """
    sObj = get_authenticated_client(access_token)
    user = sObj.getCurrentUser()

    user_info = {
        'id': user.getId(),
        'name': f"{user.getFirstName()} {user.getLastName()}",
        'email': user.getEmail(),
        'picture': user.getPicture().getMedium() if user.getPicture() else None
    }

    logger.info("Fetched user info for user_id=%s", user_info['id'])
    return user_info


def fetch_user_data(access_token):
    """
    Fetch and store all user data from Splitwise (friends, groups, expenses).

    Paginates through the Splitwise API to retrieve all expenses and stores
    everything in MongoDB collections keyed by user_id.

    Args:
        access_token: User's access token.

    Returns:
        dict: Summary statistics of fetched data.
    """
    sObj = get_authenticated_client(access_token)
    db = get_db()

    current_user = sObj.getCurrentUser()
    friends = sObj.getFriends()
    groups = sObj.getGroups()

    user_id = current_user.getId()

    # Store user details
    user_data = {
        'user_id': user_id,
        'first_name': current_user.getFirstName(),
        'last_name': current_user.getLastName(),
        'email': current_user.getEmail()
    }
    db.users.update_one({'user_id': user_id}, {'$set': user_data}, upsert=True)

    def update_user_collection(collection_name, data):
        """Replace a user-specific collection with fresh data."""
        collection = db[f'{user_id}_{collection_name}']
        collection.delete_many({})
        if data:
            collection.insert_many(data)
        logger.debug("Updated %s collection for user %s: %d records",
                      collection_name, user_id, len(data))

    # Store groups
    group_data = [
        {
            'group_id': group.getId(),
            'name': group.getName(),
            'updated_at': group.getUpdatedAt()
        } for group in groups
    ]
    update_user_collection('groups', group_data)

    # Store friends
    friend_data = [
        {
            'friend_id': friend.getId(),
            'first_name': friend.getFirstName(),
            'last_name': friend.getLastName(),
            'email': friend.getEmail()
        } for friend in friends
    ]
    update_user_collection('friends', friend_data)

    # Fetch all expenses with pagination
    all_expenses = []
    offset = 0
    limit = 100
    while True:
        expenses = sObj.getExpenses(limit=limit, offset=offset)
        if not expenses:
            break
        all_expenses.extend(expenses)
        offset += limit
        if len(expenses) < limit:
            break

    # Process and store expenses
    expense_data = []
    for expense in all_expenses:
        created_by = "Unknown"
        if expense.getCreatedBy():
            first_name = expense.getCreatedBy().getFirstName() or ""
            last_name = expense.getCreatedBy().getLastName() or ""
            created_by = f"{first_name} {last_name}".strip() or "Unknown"

        # Calculate net amount for the current user
        net_amount = 0
        for user in expense.getUsers():
            if user.getId() == current_user.getId():
                net_amount = user.getNetBalance()
                break

        expense_data.append({
            'expense_id': expense.getId(),
            'description': expense.getDescription(),
            'total_cost': expense.getCost(),
            'net_amount': net_amount,
            'currency_code': expense.getCurrencyCode(),
            'date': expense.getDate(),
            'created_by': created_by,
            'deleted_at': expense.getDeletedAt()
        })
    update_user_collection('expenses', expense_data)

    summary = {
        'user_id': user_id,
        'friends_count': len(friends),
        'groups_count': len(groups),
        'expenses_count': len(all_expenses)
    }

    logger.info(
        "Data fetch complete for user %s: %d friends, %d groups, %d expenses",
        user_id, len(friends), len(groups), len(all_expenses)
    )

    return summary
