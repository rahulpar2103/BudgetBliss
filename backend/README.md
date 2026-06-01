# BudgetBliss Backend

Flask-based REST API for the BudgetBliss expense management platform. Handles Splitwise OAuth authentication, expense data synchronization, ML-powered expense categorization, and analytics.

## Architecture

```
backend/
├── app/                          # Application package
│   ├── __init__.py               # Flask app factory
│   ├── config.py                 # Environment-based configuration
│   ├── extensions.py             # Database initialization
│   ├── routes/                   # API Blueprint modules
│   │   ├── auth.py               # OAuth endpoints
│   │   ├── expenses.py           # Expense CRUD & processing
│   │   ├── analytics.py          # Visualizations & ML metrics
│   │   └── users.py              # User profile & stats
│   ├── services/                 # Business logic layer
│   │   ├── splitwise_service.py  # Splitwise SDK wrapper
│   │   ├── expense_service.py    # Expense operations
│   │   └── ml_service.py         # ML pipeline & evaluation
│   └── utils/                    # Shared utilities
│       ├── logging_config.py     # Structured logging
│       └── helpers.py            # Formatters & converters
├── ml/                           # Machine learning artifacts
│   ├── evaluate.py               # Standalone evaluation script
│   ├── training_data/            # Training dataset
│   └── saved_models/             # Persisted model files
├── tests/                        # Unit tests
├── run.py                        # Application entry point
├── requirements.txt              # Pinned dependencies
└── .env.example                  # Environment variable template
```

## Setup

```bash
# 1. Create virtual environment
py -m venv venv
venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Splitwise API keys and MongoDB URI

# 4. Train the ML model
py -m ml.evaluate

# 5. Run the server
py run.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/authorize` | Initiate Splitwise OAuth |
| POST | `/api/callback` | Exchange OAuth tokens |
| POST | `/api/fetch_data` | Sync data from Splitwise |
| POST | `/api/process_expenses` | Run ML categorization |
| GET | `/api/get_results` | Get categorized results |
| POST | `/api/add_expense` | Add manual expense |
| GET | `/api/user_info` | Get user profile |
| GET | `/api/user_stats` | Get aggregate statistics |
| GET | `/api/ml/metrics` | Get ML model metrics |
| POST | `/api/ml/retrain` | Retrain the ML model |
| GET | `/api/plot/expense_distribution` | Bar chart visualization |
| GET | `/api/plot/expense_pie_chart` | Pie chart visualization |
