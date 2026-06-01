"""
Standalone ML model evaluation script.

Run this to train the model, evaluate it, and print a comprehensive
metrics report. Useful for validating model changes or generating
numbers for documentation/README.

Usage:
    cd backend
    python -m ml.evaluate

Output:
    - Console: Formatted metrics report
    - File: ml/saved_models/metrics.json
    - File: ml/saved_models/pipeline.joblib
    - File: ml/saved_models/label_encoder.joblib
"""

import os
import sys
import json

# Add backend directory to path so we can import app modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

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
import joblib
from datetime import datetime


def clean_description(desc):
    """Clean an expense description by removing single-character tokens."""
    return ' '.join(word for word in str(desc).split() if len(word) > 1)


def run_evaluation():
    """Train, evaluate, and persist the expense categorization model."""
    # Set stdout and stderr to UTF-8 to prevent encoding errors on Windows when printing emojis
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # Paths
    training_data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'training_data', 'training-data.csv'
    )
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saved_models')
    os.makedirs(model_dir, exist_ok=True)

    print("=" * 70)
    print("  BudgetBliss — ML Model Evaluation Report")
    print("=" * 70)

    # Load data
    data = pd.read_csv(training_data_path)
    data['Description'] = data['Description'].fillna('Unknown').apply(clean_description)
    valid_mask = (data['Description'].str.strip() != '') & (data['Description'] != 'Unknown')
    data = data[valid_mask].copy()

    X = data['Description'].values
    y = data['expense_type'].values

    print(f"\n📊 Dataset Summary")
    print(f"   Total samples:  {len(X)}")
    print(f"   Categories:     {len(set(y))}")
    print(f"   Category dist:  {dict(pd.Series(y).value_counts())}")

    # Encode
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    category_names = list(le.classes_)

    # Check class counts to decide on stratification
    class_counts = pd.Series(y).value_counts()
    min_class_count = class_counts.min()

    # --- Holdout Evaluation (80/20) ---
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
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_w = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_m = f1_score(y_test, y_pred, average='macro', zero_division=0)

    print(f"\n📈 Holdout Evaluation (80/20 split)")
    print(f"   Accuracy:           {acc:.2%}")
    print(f"   Precision (wt):     {prec:.2%}")
    print(f"   Recall (wt):        {rec:.2%}")
    print(f"   F1-Score (wt):      {f1_w:.2%}")
    print(f"   F1-Score (macro):   {f1_m:.2%}")

    print(f"\n📋 Per-Category Performance")
    print(classification_report(y_test, y_pred, labels=list(range(len(category_names))), target_names=category_names, zero_division=0))

    # --- Cross-Validation ---
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
        scoring=['accuracy', 'f1_weighted'],
        return_train_score=False
    )

    print(f"\n🔄 5-Fold Stratified Cross-Validation")
    print(f"   Accuracy:  {cv_results['test_accuracy'].mean():.2%} ± {cv_results['test_accuracy'].std():.2%}")
    print(f"   F1 (wt):   {cv_results['test_f1_weighted'].mean():.2%} ± {cv_results['test_f1_weighted'].std():.2%}")
    print(f"   Per-fold:  {[f'{x:.2%}' for x in cv_results['test_accuracy']]}")

    # --- Confusion Matrix ---
    cm = confusion_matrix(y_test, y_pred, labels=list(range(len(category_names))))
    print(f"\n🔀 Confusion Matrix")
    print(f"   Labels: {category_names}")
    for row in cm:
        print(f"   {row}")

    # --- Train production model on all data ---
    prod_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english', min_df=2)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    prod_pipeline.fit(X, y_encoded)

    # --- Save ---
    joblib.dump(prod_pipeline, os.path.join(model_dir, 'pipeline.joblib'))
    joblib.dump(le, os.path.join(model_dir, 'label_encoder.joblib'))

    # Per-category F1
    per_cat_f1 = {}
    cat_f1 = f1_score(y_test, y_pred, labels=list(range(len(category_names))), average=None, zero_division=0)
    for i, name in enumerate(category_names):
        if i < len(cat_f1):
            per_cat_f1[name] = round(cat_f1[i], 4)

    metrics = {
        'model_type': 'TF-IDF + RandomForest (n_estimators=100)',
        'training_samples': int(len(X)),
        'categories': category_names,
        'num_categories': len(category_names),
        'holdout_metrics': {
            'accuracy': round(acc, 4),
            'precision_weighted': round(prec, 4),
            'recall_weighted': round(rec, 4),
            'f1_weighted': round(f1_w, 4),
            'f1_macro': round(f1_m, 4),
        },
        'per_category_f1': per_cat_f1,
        'cross_validation': {
            'folds': 5,
            'accuracy_mean': round(cv_results['test_accuracy'].mean(), 4),
            'accuracy_std': round(cv_results['test_accuracy'].std(), 4),
            'f1_weighted_mean': round(cv_results['test_f1_weighted'].mean(), 4),
            'f1_weighted_std': round(cv_results['test_f1_weighted'].std(), 4),
        },
        'confusion_matrix': {
            'matrix': cm.tolist(),
            'labels': category_names
        },
        'trained_at': datetime.now().isoformat(),
        'model_version': '1.0.0',
    }

    metrics_path = os.path.join(model_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✅ Model saved to:   {model_dir}/")
    print(f"   Metrics saved to: {metrics_path}")
    print("=" * 70)

    return metrics


if __name__ == '__main__':
    run_evaluation()
