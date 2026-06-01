"""
Machine Learning service for expense categorization.

Implements a TF-IDF + Random Forest classification pipeline with
comprehensive evaluation metrics. This is the core differentiator
of BudgetBliss — it auto-categorizes expenses based on description text.

Pipeline:
    1. Text preprocessing (cleaning, stopword removal)
    2. TF-IDF vectorization
    3. Random Forest classification (100 estimators)
    4. Model evaluation with cross-validation
    5. Model persistence with joblib

Metrics tracked:
    - Accuracy, Precision, Recall, F1-Score (weighted & macro)
    - Per-category F1 breakdown
    - 5-fold Stratified Cross-Validation scores
    - Confusion matrix
"""

import logging
import os
import json
from datetime import datetime

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from app.extensions import get_db
from app.utils.helpers import decimal128_to_float

logger = logging.getLogger(__name__)

# Module-level cache for loaded model
_cached_pipeline = None
_cached_label_encoder = None
_cached_metrics = None


def clean_description(desc):
    """
    Clean an expense description by removing single-character tokens.

    Args:
        desc: Raw description string.

    Returns:
        Cleaned description with short tokens removed.
    """
    return ' '.join(word for word in str(desc).split() if len(word) > 1)


def _get_model_paths(app_config=None):
    """Get paths for saved model artifacts."""
    if app_config is None:
        from app.config import settings
        app_config = settings

    if hasattr(app_config, 'MODEL_DIR'):
        model_dir = app_config.MODEL_DIR
    elif isinstance(app_config, dict):
        model_dir = app_config.get('MODEL_DIR')
    else:
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'saved_models')

    os.makedirs(model_dir, exist_ok=True)

    return {
        'pipeline': os.path.join(model_dir, 'pipeline.joblib'),
        'label_encoder': os.path.join(model_dir, 'label_encoder.joblib'),
        'metrics': os.path.join(model_dir, 'metrics.json'),
    }


def train_and_evaluate(training_data_path=None, app_config=None):
    """
    Train the expense categorization model and compute evaluation metrics.

    Performs:
        1. Load and preprocess training data
        2. Train/test split (80/20) for holdout evaluation
        3. 5-fold stratified cross-validation for robust metrics
        4. Full training on all data for production model
        5. Persist model and metrics to disk

    Args:
        training_data_path: Path to the training CSV file.
        app_config: Configuration dict or object (optional).

    Returns:
        dict: Comprehensive metrics report.
    """
    global _cached_pipeline, _cached_label_encoder, _cached_metrics

    # Resolve paths
    if training_data_path is None:
        if app_config is None:
            from app.config import settings
            app_config = settings

        if hasattr(app_config, 'TRAINING_DATA_PATH'):
            training_data_path = app_config.TRAINING_DATA_PATH
        elif isinstance(app_config, dict):
            training_data_path = app_config.get('TRAINING_DATA_PATH')

        if training_data_path is None:
            training_data_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'ml', 'training_data', 'training-data.csv'
            )

    paths = _get_model_paths(app_config)

    # --- Load & preprocess training data ---
    logger.info("Loading training data from %s", training_data_path)
    data = pd.read_csv(training_data_path)
    data['Description'] = data['Description'].fillna('Unknown').apply(clean_description)

    # Filter out rows with empty/unknown descriptions
    valid_mask = (data['Description'].str.strip() != '') & (data['Description'] != 'Unknown')
    data = data[valid_mask].copy()

    X = data['Description'].values
    y = data['expense_type'].values

    logger.info(
        "Training data: %d samples, %d categories: %s",
        len(X), len(set(y)), sorted(set(y))
    )

    # --- Encode labels ---
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    category_names = list(le.classes_)

    # Check class counts to decide on stratification
    class_counts = pd.Series(y).value_counts()
    min_class_count = class_counts.min()

    # --- Holdout evaluation (80/20 split) ---
    if min_class_count >= 2:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )

    holdout_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    holdout_pipeline.fit(X_train, y_train)
    y_pred = holdout_pipeline.predict(X_test)

    holdout_metrics = {
        'accuracy': round(accuracy_score(y_test, y_pred), 4),
        'precision_weighted': round(precision_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'recall_weighted': round(recall_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'f1_weighted': round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'f1_macro': round(f1_score(y_test, y_pred, average='macro', zero_division=0), 4),
    }

    # Per-category F1
    per_category_f1 = {}
    category_f1_scores = f1_score(y_test, y_pred, average=None, labels=list(range(len(category_names))), zero_division=0)
    for i, cat_name in enumerate(category_names):
        if i < len(category_f1_scores):
            per_category_f1[cat_name] = round(category_f1_scores[i], 4)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=list(range(len(category_names))))
    cm_dict = {
        'matrix': cm.tolist(),
        'labels': category_names
    }

    # Classification report
    cls_report = classification_report(y_test, y_pred, labels=list(range(len(category_names))), target_names=category_names, zero_division=0)
    logger.info("Holdout classification report:\n%s", cls_report)

    # --- Cross-validation (5-fold stratified) ---
    cv_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    n_splits = 5
    if min_class_count >= n_splits:
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    else:
        from sklearn.model_selection import KFold
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        
    cv_results = cross_validate(
        cv_pipeline, X, y_encoded, cv=cv,
        scoring=['accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted'],
        return_train_score=False
    )

    cross_val_metrics = {
        'folds': 5,
        'accuracy_mean': round(cv_results['test_accuracy'].mean(), 4),
        'accuracy_std': round(cv_results['test_accuracy'].std(), 4),
        'f1_weighted_mean': round(cv_results['test_f1_weighted'].mean(), 4),
        'f1_weighted_std': round(cv_results['test_f1_weighted'].std(), 4),
        'precision_weighted_mean': round(cv_results['test_precision_weighted'].mean(), 4),
        'recall_weighted_mean': round(cv_results['test_recall_weighted'].mean(), 4),
        'per_fold_accuracy': [round(x, 4) for x in cv_results['test_accuracy'].tolist()],
    }

    # --- Train final production model on ALL data ---
    production_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    production_pipeline.fit(X, y_encoded)

    # --- Compile full metrics report ---
    metrics_report = {
        'model_type': 'TF-IDF + RandomForest (n_estimators=100)',
        'training_samples': int(len(X)),
        'categories': category_names,
        'num_categories': len(category_names),
        'holdout_metrics': holdout_metrics,
        'per_category_f1': per_category_f1,
        'cross_validation': cross_val_metrics,
        'confusion_matrix': cm_dict,
        'trained_at': datetime.now().isoformat(),
        'model_version': '1.0.0',
    }

    # --- Persist model and metrics ---
    joblib.dump(production_pipeline, paths['pipeline'])
    joblib.dump(le, paths['label_encoder'])
    with open(paths['metrics'], 'w') as f:
        json.dump(metrics_report, f, indent=2)

    logger.info(
        "Model trained and saved. Holdout accuracy=%.2f%%, CV accuracy=%.2f%% ± %.2f%%",
        holdout_metrics['accuracy'] * 100,
        cross_val_metrics['accuracy_mean'] * 100,
        cross_val_metrics['accuracy_std'] * 100
    )

    # Update cache
    _cached_pipeline = production_pipeline
    _cached_label_encoder = le
    _cached_metrics = metrics_report

    return metrics_report


def _load_model(app_config=None):
    """Load persisted model from disk, training if not found."""
    global _cached_pipeline, _cached_label_encoder, _cached_metrics

    if _cached_pipeline is not None and _cached_label_encoder is not None:
        return _cached_pipeline, _cached_label_encoder

    paths = _get_model_paths(app_config)

    if os.path.exists(paths['pipeline']) and os.path.exists(paths['label_encoder']):
        _cached_pipeline = joblib.load(paths['pipeline'])
        _cached_label_encoder = joblib.load(paths['label_encoder'])
        if os.path.exists(paths['metrics']):
            with open(paths['metrics'], 'r') as f:
                _cached_metrics = json.load(f)
        logger.info("Loaded persisted model from disk")
        return _cached_pipeline, _cached_label_encoder

    # No saved model — train from scratch
    logger.info("No saved model found, training from scratch...")
    train_and_evaluate(app_config=app_config)
    return _cached_pipeline, _cached_label_encoder


def get_metrics(app_config=None):
    """
    Get the current model's evaluation metrics.

    Returns cached metrics if available, otherwise loads from disk
    or trains a fresh model.

    Returns:
        dict: Metrics report.
    """
    global _cached_metrics

    if _cached_metrics is not None:
        return _cached_metrics

    paths = _get_model_paths(app_config)
    if os.path.exists(paths['metrics']):
        with open(paths['metrics'], 'r') as f:
            _cached_metrics = json.load(f)
        return _cached_metrics

    # Need to train to get metrics
    return train_and_evaluate(app_config=app_config)


def process_expenses(user_id, app_config=None):
    """
    Categorize a user's expenses using the trained ML model.

    Loads the user's expenses from MongoDB, runs them through the
    TF-IDF + RandomForest pipeline, and stores predictions back.

    This preserves the original logic from Expense.py while using
    the persisted model instead of retraining every time.

    Args:
        user_id: The Splitwise user ID.
        app_config: Flask app config dict (optional).

    Returns:
        dict: Summary with prediction count and categories found.
    """
    db = get_db()
    pipeline, le = _load_model(app_config)

    # Load user's expenses
    expenses = list(db[f'{user_id}_expenses'].find())
    logger.info("Processing %d expenses for user %s", len(expenses), user_id)

    if not expenses:
        logger.warning("No expenses found for user %s", user_id)
        return {'predictions': 0, 'categories': []}

    # Preprocess expense descriptions
    for item in expenses:
        original_desc = item.get('Description') or item.get('description', '')
        if not original_desc:
            original_desc = f"{item.get('Created By', item.get('created_by', ''))} - {item.get('Cost', item.get('total_cost', ''))} {item.get('Currency Code', item.get('currency_code', ''))}"
        item['_cleaned_desc'] = clean_description(original_desc)

        # Normalize cost field
        cost = item.get('Cost') or item.get('total_cost', 0)
        item['_cost'] = decimal128_to_float(cost)

        # Check for payment type
        expense_type = item.get('expense_type', item.get('description', ''))
        item['_is_payment'] = str(expense_type).lower() in ('payment', 'settle all balances')

    # Filter to expenses with valid descriptions
    valid_expenses = [e for e in expenses if e['_cleaned_desc'].strip() and e['_cleaned_desc'] != 'Unknown']

    if not valid_expenses:
        logger.warning("No valid descriptions found in user %s expenses", user_id)
        return {'predictions': 0, 'categories': []}

    # Predict
    X_test = [e['_cleaned_desc'] for e in valid_expenses]
    predictions = pipeline.predict(X_test)

    # Build results
    results = []
    for expense, prediction in zip(valid_expenses, predictions):
        result = {k: v for k, v in expense.items() if not k.startswith('_')}
        result['predicted_expense_type'] = le.inverse_transform([prediction])[0]
        if expense['_is_payment']:
            result['predicted_expense_type'] = 'Payment'
        results.append(result)

    logger.info("Generated %d predictions for user %s", len(results), user_id)

    # Compute expense sums (paid vs owed)
    expense_sums_paid = {}
    expense_sums_owed = {}
    for result, expense in zip(results, valid_expenses):
        exp_type = result['predicted_expense_type']
        amount = expense['_cost']
        if amount > 0:
            expense_sums_paid[exp_type] = expense_sums_paid.get(exp_type, 0) + amount
        else:
            expense_sums_owed[exp_type] = expense_sums_owed.get(exp_type, 0) + abs(amount)

    # Merge into summary records
    all_types = set(list(expense_sums_paid.keys()) + list(expense_sums_owed.keys()))
    expense_sums = [
        {
            'predicted_expense_type': exp_type,
            'Paid Amount': round(expense_sums_paid.get(exp_type, 0), 2),
            'Owed Amount': round(expense_sums_owed.get(exp_type, 0), 2)
        }
        for exp_type in sorted(all_types)
    ]

    logger.info("Expense sums: %d categories for user %s", len(expense_sums), user_id)

    # Save results to MongoDB
    db[f'{user_id}_predictions'].delete_many({})
    if results:
        db[f'{user_id}_predictions'].insert_many(results)

    db[f'{user_id}_expense_sums'].delete_many({})
    if expense_sums:
        db[f'{user_id}_expense_sums'].insert_many(expense_sums)

    logger.info("Predictions and expense sums saved for user %s", user_id)

    return {
        'predictions': len(results),
        'categories': list(all_types)
    }
