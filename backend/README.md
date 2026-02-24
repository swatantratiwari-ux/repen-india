# RePen India — Backend API

Production-ready FastAPI backend for the RePen India pen recycling platform.

## Tech Stack

| Layer          | Technology                  |
| -------------- | --------------------------- |
| Framework      | FastAPI                     |
| ORM            | SQLAlchemy 2.0              |
| Database       | PostgreSQL                  |
| Migrations     | Alembic                     |
| Auth           | JWT (python-jose) + bcrypt  |
| Validation     | Pydantic v2                 |

---

## Folder Structure

```
backend/
├── alembic/                  # Database migration environment
│   ├── env.py                # Alembic config (auto-imports models)
│   ├── script.py.mako        # Migration template
│   └── versions/             # Generated migration files
├── app/
│   ├── core/
│   │   ├── config.py         # Pydantic settings (from .env)
│   │   ├── database.py       # Engine, session, Base, get_db
│   │   └── security.py       # JWT, bcrypt, auth dependencies
│   ├── models/
│   │   ├── institution.py    # Institution ORM model
│   │   ├── collection_request.py  # CollectionRequest ORM model
│   │   └── admin.py          # Admin ORM model
│   ├── schemas/
│   │   ├── institution.py    # Institution Pydantic schemas
│   │   ├── collection_request.py  # Collection Pydantic schemas
│   │   ├── admin.py          # Admin Pydantic schemas
│   │   └── token.py          # JWT token schemas
│   ├── routes/
│   │   ├── institutions.py   # /register, /login, /me, /dashboard
│   │   ├── collections.py    # CRUD for collection requests
│   │   └── admin.py          # Admin login, manage institutions
│   ├── scripts/
│   │   └── seed_admin.py     # Create initial admin account
│   └── main.py               # FastAPI app factory
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/rependb
#   JWT_SECRET_KEY=your-random-secret-key
```

### 5. Create PostgreSQL Database

```sql
CREATE DATABASE rependb;
CREATE USER repenuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE rependb TO repenuser;
```

### 6. Run Database Migrations

```bash
# Generate initial migration from models
alembic revision --autogenerate -m "initial_tables"

# Apply migrations
alembic upgrade head
```

### 7. Seed Admin Account

```bash
# Via environment variables
ADMIN_EMAIL=admin@repenindia.in ADMIN_PASSWORD=YourSecurePass123! python -m app.scripts.seed_admin

# Or interactively
python -m app.scripts.seed_admin
```

### 8. Start the Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Endpoints

### Institutions

| Method | Endpoint                         | Auth     | Description            |
| ------ | -------------------------------- | -------- | ---------------------- |
| POST   | `/api/v1/institutions/register`  | Public   | Register institution   |
| POST   | `/api/v1/institutions/login`     | Public   | Login, get JWT         |
| GET    | `/api/v1/institutions/me`        | JWT      | Get profile            |
| GET    | `/api/v1/institutions/dashboard` | JWT      | Dashboard stats        |

### Collections

| Method | Endpoint                              | Auth     | Description              |
| ------ | ------------------------------------- | -------- | ------------------------ |
| POST   | `/api/v1/collections/`                | JWT      | Create pickup request    |
| GET    | `/api/v1/collections/`                | JWT      | List my requests         |
| GET    | `/api/v1/collections/{id}`            | JWT      | Get single request       |

### Admin

| Method | Endpoint                                         | Auth  | Description            |
| ------ | ------------------------------------------------ | ----- | ---------------------- |
| POST   | `/api/v1/admin/login`                            | Public| Admin login            |
| GET    | `/api/v1/admin/institutions`                     | Admin | List all institutions  |
| PATCH  | `/api/v1/admin/collections/{id}/status`          | Admin | Update request status  |

### Health

| Method | Endpoint   | Description    |
| ------ | ---------- | -------------- |
| GET    | `/health`  | Health check   |

---

## Interactive Docs

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Production Deployment Notes

1. **Never commit `.env`** — use `.env.example` as a template only.
2. **Generate a strong JWT secret**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```
3. **Use Gunicorn with Uvicorn workers** in production:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. **Enable PostgreSQL connection pooling** (PgBouncer) for high traffic.
5. **Set `APP_ENV=production`** and `APP_DEBUG=false` in production `.env`.
6. **Run behind a reverse proxy** (Nginx/Caddy) with HTTPS.
7. **Docker deployment**:
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
   ```
8. **Set up health check monitoring** via the `/health` endpoint.
9. **Use Alembic for all schema changes** — never modify production tables manually.
