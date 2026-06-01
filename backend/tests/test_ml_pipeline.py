"""
Unit tests for the ML pipeline.

Validates that the model trains successfully, produces valid metrics,
and the prediction pipeline works end-to-end.
"""

import os
import json
import pytest
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Path to training data
TRAINING_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'ml', 'training_data', 'training-data.csv'
)


def clean_description(desc):
    """Clean an expense description by removing single-character tokens."""
    return ' '.join(word for word in str(desc).split() if len(word) > 1)


@pytest.fixture
def training_data():
    """Load and preprocess training data."""
    data = pd.read_csv(TRAINING_DATA_PATH)
    data['Description'] = data['Description'].fillna('Unknown').apply(clean_description)
    valid_mask = (data['Description'].str.strip() != '') & (data['Description'] != 'Unknown')
    return data[valid_mask].copy()


class TestDataQuality:
    """Tests for training data quality and integrity."""

    def test_training_data_exists(self):
        """Training data CSV file should exist."""
        assert os.path.exists(TRAINING_DATA_PATH), f"Training data not found at {TRAINING_DATA_PATH}"

    def test_minimum_sample_count(self, training_data):
        """Should have at least 50 training samples."""
        assert len(training_data) >= 50, f"Only {len(training_data)} samples — need at least 50"

    def test_required_columns_present(self, training_data):
        """Training data must have Description and expense_type columns."""
        assert 'Description' in training_data.columns
        assert 'expense_type' in training_data.columns

    def test_no_empty_labels(self, training_data):
        """All rows should have a non-empty expense_type label."""
        assert training_data['expense_type'].notna().all()
        assert (training_data['expense_type'].str.strip() != '').all()

    def test_multiple_categories(self, training_data):
        """Should have at least 3 distinct expense categories."""
        categories = training_data['expense_type'].nunique()
        assert categories >= 3, f"Only {categories} categories — need at least 3"


class TestMLPipeline:
    """Tests for the ML training and prediction pipeline."""

    def test_pipeline_trains_successfully(self, training_data):
        """Pipeline should train without errors."""
        X = training_data['Description'].values
        y = training_data['expense_type'].values

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        # Should not raise
        pipeline.fit(X, y_encoded)

    def test_predictions_have_correct_shape(self, training_data):
        """Predictions should have same length as input."""
        X = training_data['Description'].values
        y = training_data['expense_type'].values

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        pipeline.fit(X, y_encoded)

        predictions = pipeline.predict(X)
        assert len(predictions) == len(X)

    def test_holdout_accuracy_above_threshold(self, training_data):
        """Model should achieve at least 50% accuracy on holdout set."""
        X = training_data['Description'].values
        y = training_data['expense_type'].values

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        # Check class counts to decide on stratification
        class_counts = pd.Series(y).value_counts()
        min_class_count = class_counts.min()

        if min_class_count >= 2:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        assert acc >= 0.50, f"Accuracy {acc:.2%} is below 50% threshold"

    def test_inverse_transform_produces_valid_labels(self, training_data):
        """Predicted labels should map back to known category names."""
        X = training_data['Description'].values
        y = training_data['expense_type'].values
        known_categories = set(y)

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        pipeline.fit(X, y_encoded)

        predictions = pipeline.predict(X[:5])
        predicted_labels = le.inverse_transform(predictions)

        for label in predicted_labels:
            assert label in known_categories, f"Unknown predicted label: {label}"
