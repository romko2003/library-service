# Library Service (Django REST)

An online library management system: books inventory, customer borrowings, payments (Stripe), fines for overdue returns, and optional Telegram notifications. The API is self-documented (Swagger) and protected with JWT. Docker support is included.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started (Local)](#getting-started-local)
- [Environment Variables](#environment-variables)
- [Run with Docker](#run-with-docker)
- [Migrations & Admin](#migrations--admin)
- [API Docs](#api-docs)
- [Authentication](#authentication)
- [Endpoints Overview](#endpoints-overview)
- [Payment Flow (Stripe)](#payment-flow-stripe)
- [Testing](#testing)
- [Code Style & Comments](#code-style--comments)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features
- **Users**: registration, JWT tokens, `/me` endpoint.
- **Books**: CRUD with permissions (only staff can create/update/delete).
- **Borrowings**: create borrowing (decreases inventory), list/detail with filters, return borrowing (increases inventory, fine if overdue).
- **Payments (Stripe)**: Checkout Session created on borrowing; success/cancel endpoints; list/detail payments.
- **Fines**: `overdue_days * daily_fee * FINE_MULTIPLIER`.
- **Docs**: OpenAPI/Swagger via `/api/docs/`.
- **Docker**: Dockerfile + docker-compose for easy run.

## Architecture
repo/
├─ .env.sample
├─ requirements.txt
├─ docker-compose.yml
└─ backend/
├─ manage.py
├─ library/ # settings/urls/asgi/wsgi
├─ users/ # custom user + auth
├─ books/ # models/serializers/views/urls
├─ borrowings/ # models/serializers/filters/views/urls
└─ payments/ # models/stripe utils/views/urls

markdown
Copy code

## Tech Stack
- **Backend**: Django 5, DRF, django-filter, SimpleJWT, drf-spectacular
- **Payments**: Stripe (test mode)
- **Infra**: Docker, docker-compose, PostgreSQL (or SQLite for local)
- **Other**: python-dotenv, requests (for Telegram helper)

## Getting Started (Local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# configure your .env (see template)
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
Environment Variables
Copy .env.sample to .env and fill in as needed:

dotenv
Copy code
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# For SQLite leave DB_HOST empty; for Postgres via Docker set:
DB_NAME=library
DB_USER=library
DB_PASSWORD=library
DB_HOST=db
DB_PORT=5432

ACCESS_MINUTES=60
REFRESH_DAYS=1
API_TITLE=Library API
API_VERSION=1.0.0

# Stripe (TEST only)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
FRONTEND_SUCCESS_URL=http://localhost:8000/api/payments/success/
FRONTEND_CANCEL_URL=http://localhost:8000/api/payments/cancel/

FINE_MULTIPLIER=2
Run with Docker
bash
Copy code
docker compose up --build
API: http://localhost:8000/api/

Swagger: http://localhost:8000/api/docs/

Migrations & Admin
bash
Copy code
# inside the web container (if needed)
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
API Docs
Swagger UI: GET /api/docs/

OpenAPI schema: GET /api/schema/

Authentication
Register: POST /api/users/

Obtain tokens: POST /api/users/token/

Refresh tokens: POST /api/users/token/refresh/

Me: GET/PUT/PATCH /api/users/me/

Send JWT in headers:

makefile
Copy code
Authorization: Bearer <ACCESS_TOKEN>
Endpoints Overview
Books
GET /api/books/ — public list

GET /api/books/{id}/ — public detail

POST /api/books/ — staff only

PUT/PATCH/DELETE /api/books/{id}/ — staff only

Borrowings
GET /api/borrowings/?is_active=true|false&user_id=<id>
Non-staff see only their borrowings; user_id is staff-only.

GET /api/borrowings/{id}/

POST /api/borrowings/ — validate stock, inventory -= 1, create Stripe payment session

POST /api/borrowings/{id}/return/ — forbid double return, inventory += 1, create fine if overdue

Payments
GET /api/payments/ — non-staff see only their payments

GET /api/payments/{id}/

GET /api/payments/success/?session_id=... — mark as PAID if Stripe says so

GET /api/payments/cancel/ — info message (session ~24h)

Payment Flow (Stripe)
User creates a borrowing → backend calculates base price (days * daily_fee) and creates a Stripe Checkout Session.

The system stores session_id and session_url in a related Payment record (type=PAYMENT).

User pays on Stripe (test card like 4242 4242 4242 4242).

Stripe redirects to /api/payments/success/?session_id=...; backend marks Payment as PAID.

If the borrowing is returned after expected_return_date, a Payment of type FINE is created:

ini
Copy code
fine = overdue_days * daily_fee * FINE_MULTIPLIER
Testing
Use pytest + pytest-django:

bash
Copy code
pytest --cov=backend --cov-report=term-missing
Recommended test coverage (custom code) ≥ 60%:

Users: register/token/me flows

Books: public GETs; staff-only create/update/delete

Borrowings: create (decrement stock, forbid when inventory=0), list filters, return (forbid double, increment stock, fine on overdue)

Payments: list/detail permissions; success marks PAID

Code Style & Comments
All code comments must be in English.

Recommended tools: flake8, black.

Keep secrets out of Git: use .env and publish .env.sample.

Troubleshooting
CORS errors: add your frontend origin in CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS.

401 Unauthorized: send Authorization: Bearer <token>.

DB connection: verify Postgres env vars when running via Docker.

License
MIT (or your preferred license).

yaml