# BudgetBliss 💰

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.9-47A248?logo=mongodb&logoColor=white)](https://mongodb.com)

An ML-powered expense management platform that integrates with **Splitwise** to automatically categorize shared expenses using Natural Language Processing and provide visual spending analytics.

---

## ✨ Key Features

- **Splitwise OAuth Integration** — Secure login via Splitwise OAuth 1.0 to sync expense data
- **ML Expense Categorization** — Auto-classifies expenses into 6 categories using TF-IDF + Random Forest
- **Real-Time Dashboard** — Summary statistics, expense tables, and category breakdowns
- **Visual Analytics** — Interactive bar charts and pie charts via Chart.js
- **Expense Management** — Add, filter, sort, and paginate expenses with category predictions
- **Model Metrics API** — Exposes accuracy, F1-score, and cross-validation results via REST endpoint

---

## 📊 ML Model Performance

The expense categorization model uses a **TF-IDF vectorizer** paired with a **Random Forest classifier** (100 estimators) trained on a balanced dataset of **5,010 labeled expense descriptions** across 6 core categories, incorporating realistic noise (typos, abbreviations, cross-category ambiguity, and vague entries).

| Metric | Score |
|--------|-------|
| **Cross-Validation Accuracy** (5-fold) | **92.12% ± 0.99%** |
| **Cross-Validation F1-Score** (weighted) | **92.16% ± 0.94%** |
| **Holdout Accuracy** (80/20 split) | **92.71%** |
| **Weighted F1-Score** | **92.75%** |
| **Macro F1-Score** | **92.75%** |
| **Training Samples** | 5,010 |
| **Categories** | 6 (food, transportation, education, entertainment, payment, miscellaneous) |

> Run `cd backend && py -m ml.evaluate` to recompute all metrics and populate this table with updated values. The script outputs a detailed report and saves metrics to `ml/saved_models/metrics.json`.

### Category Distribution
| Category | Count | Description |
|----------|-------|-------------|
| Food | 835 | Restaurants, meals, snacks, groceries, delivery |
| Transportation | 835 | Cabs, autos, uber, ola rides, metro, flights |
| Education | 835 | Textbooks, printouts, lab manuals, stationery, courses |
| Entertainment | 835 | Movies, concert tickets, bowling, streaming, gaming |
| Payment | 835 | Splitwise settlements, repaying friends, UPI transfers |
| Miscellaneous | 835 | Laundry, mobile recharges, pharmacy, bills, gifts |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  Homepage │ Login │ Dashboard │ Expenses │ Visualizations │
│                      (Chart.js)                          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / REST API
┌──────────────────────┴──────────────────────────────────┐
│                  FastAPI Backend                        │
│                                                          │
│  ┌─── Routes (APIRouters) ───┐  ┌─── Services ────────┐ │
│  │ auth.py     (OAuth)       │  │ splitwise_service.py │ │
│  │ expenses.py (CRUD)        │  │ expense_service.py   │ │
│  │ analytics.py (Charts/ML)  │  │ ml_service.py        │ │
│  │ users.py   (Profile)      │  │   └─ TF-IDF + RF    │ │
│  └───────────────────────────┘  └──────────────────────┘ │
│                                                          │
│  ┌─── ML Pipeline ──────────────────────────────────────┐│
│  │ Text Preprocessing → TF-IDF Vectorization            ││
│  │ → Random Forest Classification → Model Persistence   ││
│  │ → Evaluation (CV, Holdout, Per-Category F1)          ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────┐    ┌──────────────────┐
│         MongoDB                  │    │  Splitwise API   │
│  users, expenses, predictions,   │    │  (OAuth 1.0)     │
│  expense_sums, friends, groups   │    └──────────────────┘
└─────────────────────────────────┘
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **App Factory Pattern** | Enables testing with different configs, avoids circular imports |
| **Service Layer** | Separates business logic from routes for testability |
| **APIRouter Routing** | Modular route organization, auto Swagger docs (`/docs`), each domain in its own file |
| **Model Persistence** | Avoids retraining on every request (joblib serialization) |
| **Centralized DB** | Single MongoDB connection pool instead of per-file clients |
| **Structured Logging** | Replaces print() with leveled, timestamped log output |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, React Router v6, Chart.js, Axios |
| **Backend** | FastAPI, Uvicorn, Pydantic, CORS Middleware |
| **ML/NLP** | scikit-learn (TF-IDF, Random Forest, Pipeline), joblib |
| **Database** | MongoDB (PyMongo) |
| **Auth** | Splitwise OAuth 1.0 |
| **Visualization** | Chart.js (frontend), Matplotlib (backend) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (running locally on port 27017)
- Splitwise developer account ([register here](https://secure.splitwise.com/oauth_clients))

### Backend Setup
```bash
cd backend

# Create and activate virtual environment
py -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Splitwise API keys

# Train the ML model and view metrics
py -m ml.evaluate

# Start the FastAPI server
py run.py
```

### Frontend Setup
```bash
cd budget_bliss

# Install dependencies
npm install

# Start development server (proxies to FastAPI on port 5000)
npm start
```

### Running Tests
```bash
cd backend
py -m pytest tests/ -v
```

---

## 📁 Project Structure

```
BudgetBliss/
├── backend/                    # FastAPI REST API
│   ├── app/                    # Application package
│   │   ├── __init__.py         # App factory
│   │   ├── config.py           # Environment config
│   │   ├── extensions.py       # MongoDB init
│   │   ├── routes/             # API routers
│   │   ├── services/           # Business logic
│   │   └── utils/              # Helpers & logging
│   ├── ml/                     # ML artifacts
│   │   ├── evaluate.py         # Evaluation script
│   │   ├── training_data/      # Training CSV
│   │   └── saved_models/       # Persisted models
│   ├── tests/                  # Unit tests
│   ├── run.py                  # Entry point
│   └── requirements.txt        # Dependencies
├── budget_bliss/               # React frontend
│   ├── src/
│   │   ├── Pages/              # Page components
│   │   │   ├── Dashboard.js    # Stats + predictions
│   │   │   ├── Expenses.js     # CRUD + pagination
│   │   │   ├── Visualizations.js # Charts
│   │   │   └── Profile.js      # User profile
│   │   └── components/         # Shared components
│   └── package.json
└── README.md
```

---

## 📝 License

This project was built for educational purposes as part of a software engineering curriculum.
