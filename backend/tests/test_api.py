"""
Unit tests for the BudgetBliss FastAPI API endpoints.

Tests FastAPI configurations, routers, error handling, and ML/analytics endpoints
with proper mocking for database connections and exterior Splitwise calls.
"""

import os
# Force testing environment before importing app or config
os.environ['FASTAPI_ENV'] = 'testing'
os.environ['FLASK_ENV'] = 'testing'

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from app import app
from app.config import settings


@pytest.fixture
def client():
    """A FastAPI test client for sending requests to endpoints."""
    with TestClient(app) as c:
        yield c


class TestAPIBasics:
    """Basic test suite for verifying server setup and configuration."""

    def test_app_in_testing_mode(self):
        """App should be configured for testing."""
        assert settings.TESTING is True
        assert settings.MONGODB_DB_NAME == 'budget_bliss_test'

    def test_unregistered_route_returns_404(self, client):
        """Unregistered routes should return a clean 404 response."""
        response = client.get('/api/does_not_exist')
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data or 'error' in data


class TestMLAndAnalyticsAPI:
    """Test suite for the ML and analytics-related API routes."""

    @patch('app.routes.analytics.get_metrics')
    def test_ml_metrics_endpoint(self, mock_get_metrics, client):
        """GET /api/ml/metrics should return the current ML metrics."""
        mock_metrics = {
            'model_type': 'TF-IDF + RandomForest (n_estimators=100)',
            'training_samples': 123,
            'holdout_metrics': {'accuracy': 0.92},
            'categories': ['food', 'transportation']
        }
        mock_get_metrics.return_value = mock_metrics

        response = client.get('/api/ml/metrics')
        assert response.status_code == 200
        data = response.json()
        assert data['model_type'] == 'TF-IDF + RandomForest (n_estimators=100)'
        assert data['training_samples'] == 123
        assert data['holdout_metrics']['accuracy'] == 0.92
        mock_get_metrics.assert_called_once()

    @patch('app.routes.analytics.train_and_evaluate')
    def test_ml_retrain_endpoint(self, mock_train_and_evaluate, client):
        """POST /api/ml/retrain should retrain model and return success message."""
        mock_metrics = {
            'model_type': 'TF-IDF + RandomForest (n_estimators=100)',
            'training_samples': 123,
            'holdout_metrics': {'accuracy': 0.92}
        }
        mock_train_and_evaluate.return_value = mock_metrics

        response = client.post('/api/ml/retrain')
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert data['message'] == 'Model retrained successfully'
        assert data['metrics']['holdout_metrics']['accuracy'] == 0.92
        mock_train_and_evaluate.assert_called_once()


class TestUserAndAuthAPI:
    """Test suite for authentication and user profiling endpoints."""

    def test_user_info_without_token_returns_401(self, client):
        """GET /api/user_info without Authorization header should fail with 401."""
        response = client.get('/api/user_info')
        assert response.status_code == 401
        data = response.json()
        assert 'detail' in data or 'error' in data

    @patch('app.routes.users.splitwise_service')
    def test_user_info_with_token(self, mock_splitwise_service, client):
        """GET /api/user_info with valid token should fetch profile."""
        mock_splitwise_service.fetch_user_info.return_value = {
            'id': 12345,
            'name': 'Test User',
            'email': 'test@budgetbliss.com',
            'picture': None
        }

        # Send token as serialized json in Auth header
        auth_header = {'Authorization': 'Bearer {"oauth_token": "token", "oauth_token_secret": "secret"}'}
        response = client.get('/api/user_info', headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == 12345
        assert data['name'] == 'Test User'
        mock_splitwise_service.fetch_user_info.assert_called_once()
