# 📌 `README.md`

```markdown
# 💰 Personal Finance Tracker (FastAPI + PostgreSQL + JWT + React)

A **full-stack finance tracking application** that helps users securely track their income and expenses, generate summaries, and visualize financial health.  
Built with **FastAPI** (backend), **PostgreSQL** (database), and **React** (frontend).

---

## 🚀 Features

### 🔐 Authentication

- User **registration & login** with JWT-based authentication.
- Secure password storage using **bcrypt**.
- OAuth2 password flow integration with Swagger UI.

### 💵 Transactions

- Add, view, update, and delete **income/expense transactions**.
- Category-wise reporting (`Income` / `Expense`).
- Summary endpoint with total income, total expenses, and net savings.

### 📊 Reports

- Transaction summaries for quick insights.
- (Future scope) CSV export & charts dashboard in frontend.

### 🛡️ Security

- JWT tokens for all protected APIs.
- Custom exception handling and centralized logging.
- Environment variables managed via `.env`.

---

## 📂 Project Structure
```

backend/
│── app/
│ ├── main.py # FastAPI entrypoint
│ ├── db.py # PostgreSQL connection
│ ├── db_init.py # Auto-create tables
│ ├── models/ # (Optional future models)
│ ├── routes/
│ │ ├── auth.py # Register & Login routes
│ │ ├── transactions.py # Transactions CRUD
│ ├── core/
│ │ ├── config.py # Env & app settings
│ │ ├── security.py # Password hashing & JWT utils
│ │ ├── exceptions.py # Custom exception handlers
│ ├── utils/
│ │ ├── logger.py # Logging setup
│ ├── schemas.py # Pydantic request/response schemas
│
│── requirements.txt # Backend dependencies
│
frontend/ # React frontend (WIP)
database/ # Alembic migrations (optional)
.env # Environment variables
docker-compose.yml # (Future scope: deployment)

````

---

## ⚙️ Tech Stack

- **Backend:** FastAPI, Psycopg2 (PostgreSQL driver), Pydantic, JWT (python-jose)
- **Database:** PostgreSQL
- **Frontend:** React (WIP)
- **Auth:** OAuth2PasswordBearer + JWT
- **Security:** Passlib (bcrypt hashing)
- **DevOps:** Docker (future), Alembic (optional migrations)
- **Testing:** Pytest, HTTPX (future)

---

## 🔧 Setup & Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Personal-Finance-Tracker.git
cd Personal-Finance-Tracker
````

### 2️⃣ Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)

pip install -r requirements.txt
```

### 3️⃣ Configure `.env`

Create a `.env` file in the root:

```ini
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/finance_db
JWT_SECRET="your_strong_secret_here"
JWT_ALGORITHM="HS256"
JWT_EXPIRY_MINUTES="60"
LOG_LEVEL="DEBUG"
```

### 4️⃣ Start PostgreSQL

```bash
psql -U postgres
CREATE DATABASE finance_db;
```

### 5️⃣ Run backend

```bash
uvicorn app.main:app --reload
```

Backend runs at 👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)
Swagger docs 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📌 API Endpoints

### Auth

- `POST /auth/register` → Register new user
- `POST /auth/login` → Login & get JWT

### Transactions

- `POST /transactions/` → Add a transaction
- `GET /transactions/` → Get all user transactions
- `GET /transactions/summary` → Get summary

---

## 🧑‍💻 Example Usage

```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "amogh", "password": "mypassword"}'

# Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=amogh&password=mypassword"

# Add transaction (JWT required)
curl -X POST http://127.0.0.1:8000/transactions/ \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 2000, "category": "Income", "description": "Salary"}'
```

---

## 📊 Roadmap

- [x] User registration & login
- [x] JWT-based authentication
- [x] Transactions CRUD
- [ ] Transaction update & delete APIs
- [ ] Reports with charts (React frontend)
- [ ] Docker deployment
- [ ] CSV export

---

## 👨‍💻 Author

**Amogh Pathak**
📧 [amogh9792@gmail.com](mailto:amogh9792@gmail.com)
🌐 [GitHub](https://github.com/amogh9792) | [LinkedIn](https://linkedin.com/in/amogh9792)

---

## 📝 License

MIT License. Free to use and modify.

```

---

✅ This README:
- Professional & recruiter-friendly.
- Highlights **tech stack + features + setup steps**.
- Includes **cURL usage examples**.
- Shows **roadmap** to demonstrate growth potential.

```
