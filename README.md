# 🛡️ TrustScore API

A **rule-based risk scoring engine** built with Django & Django REST Framework. Evaluates user behavior data against dynamic rules and calculates a trust score (0–100).

> 🚀 **Live Demo:** [https://trustscore-api-3joi.onrender.com](https://trustscore-api-3joi.onrender.com)

---

## ✨ Features

- Accept user activity data and calculate a trust score
- Dynamic risk rules stored in database — add/remove rules without code changes
- Evaluation history stored for audit purposes
- Clean architecture — scoring logic separated from views
- Input validation and proper error handling

---

## 📡 API Endpoints

### `POST /api/evaluate-user/`

Evaluate a user's risk based on their activity data.

**Request Body:**
```json
{
  "user_id": "U123",
  "account_age_days": 5,
  "failed_logins": 6,
  "transactions_last_24h": 30,
  "ip_changes": 4,
  "avg_transaction_amount": 7000
}
```

**Response:**
```json
{
  "trust_score": 20,
  "risk_level": "HIGH",
  "flags": [
    "New account",
    "High failed login attempts",
    "Unusual transaction volume",
    "Suspicious IP changes",
    "High average transaction amount"
  ]
}
```

### `GET /api/user-history/{user_id}/`

Retrieve evaluation history for a specific user.

**Example:** `GET /api/user-history/U123/`

---

## 📊 Risk Rules (Default)

| Condition | Threshold | Deduction | Flag |
|---|---|---|---|
| Account age < 7 days | 7 | -20 | New account |
| Failed logins > 3 | 3 | -15 | High failed login attempts |
| Transactions > 20 in 24h | 20 | -20 | Unusual transaction volume |
| IP changes > 2 | 2 | -10 | Suspicious IP changes |
| Avg transaction > 5000 | 5000 | -15 | High average transaction amount |

**Risk Levels:** 80–100 → LOW | 50–79 → MEDIUM | 0–49 → HIGH

Rules are stored in the database and can be added/modified via Django Admin without changing code.

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/Priyansh-Mandkaria/TrustScore-API.git
cd TrustScore-API
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations & seed rules
```bash
python manage.py migrate
python manage.py seed_rules
```

### 5. Start the server
```bash
python manage.py runserver
```

The API is now running at `http://127.0.0.1:8000`

---

## 🧪 Run Tests

```bash
python manage.py test scoring -v2
```

11 tests covering:
- Scoring engine unit tests (low/medium/high risk, score clamping, inactive rules)
- POST endpoint integration tests (success, validation errors)
- GET history endpoint tests

---

## 📁 Project Structure

```
├── manage.py
├── requirements.txt
├── Procfile                    # Render deployment
├── build.sh                    # Render build script
├── trustscore/                 # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── scoring/                    # Main app
    ├── models.py               # RiskRule, EvaluationRecord
    ├── services.py             # RiskScoringEngine
    ├── serializers.py          # Input/output validation
    ├── views.py                # API views
    ├── urls.py                 # URL routing
    ├── admin.py                # Django admin config
    ├── tests.py                # Test suite
    └── management/commands/
        └── seed_rules.py       # Seed default rules
```

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Django 4.2**
- **Django REST Framework 3.16**
- **SQLite** (development) — swappable with PostgreSQL for production
- **Gunicorn** (production WSGI server)

---

## 📄 License

MIT