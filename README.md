# Marketplace API

A production-oriented educational e-commerce backend built with Django + Django REST Framework.

## Stack

- Python 3.12+
- Django 5.2 LTS, Django REST Framework
- PostgreSQL
- JWT authentication (Simple JWT, refresh-token blacklist)
- django-filter
- drf-spectacular / OpenAPI / Swagger UI
- Redis + Celery for asynchronous email
- WhiteNoise for static files, Gunicorn
- Docker Compose
- pytest + pytest-django, ruff, GitHub Actions CI

## Project layout

```text
apps/
├── accounts/   # users, registration, /me, logout
├── catalog/    # categories, products, images, seed_demo command
├── cart/       # authenticated shopping cart
├── orders/     # checkout, order snapshots, stock reservation, cancellation
└── payments/   # gateway abstraction + mock gateway + async confirmation email
config/         # settings, URLs, Celery, pagination, health check
tests/          # pytest suite
```

See `architecture.md` for the design rationale and `review-checklist.md` for a review guide.

## Core business flow

```text
Register/Login → Browse products → Add to cart → Checkout
   → atomic stock validation + decrement → Order with immutable item snapshots
   → Pay (gateway) → Order PAID → Celery confirmation email
                 ↘ or Cancel / expire → stock released
```

## Important design decisions

1. **Money uses DecimalField**, never float.
2. **Checkout is transactional** and locks product rows with `select_for_update()` (in primary-key order) so concurrent checkouts cannot oversell or deadlock.
3. **OrderItem stores product name and unit price snapshots**, so historical orders never change.
4. **Cart belongs to one user** (OneToOne); the client never sends prices or totals.
5. **Product writes are staff-only**; the public sees only active products in active categories.
6. **Order and payment access is scoped to the owner**; other users get 404.
7. **Payment goes through a gateway interface**; the included provider is a mock and no card data is ever accepted or stored.
8. **The confirmation email is queued after commit** (`on_commit`, robust), so it is never sent for a rolled-back transaction and a broker outage cannot break a committed payment.
9. **Unpaid orders reserve stock**, released by cancellation or by `expire_pending_orders`.

## Local setup

```bash
cp .env.example .env            # then edit if needed
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

docker compose up -d db redis   # PostgreSQL + Redis on localhost
python manage.py migrate
python manage.py seed_demo      # optional demo catalog
python manage.py createsuperuser
python manage.py runserver
```

No Docker? Set `USE_SQLITE=1` in `.env` for a quick run (email tasks need Redis, or set `CELERY_TASK_ALWAYS_EAGER=1`).

- API docs: http://127.0.0.1:8000/api/docs/
- Admin: http://127.0.0.1:8000/admin/
- Health: http://127.0.0.1:8000/api/health/

## Docker

```bash
cp .env.example .env
docker compose up --build        # web migrates automatically on start
docker compose exec web python manage.py createsuperuser
```

Services: `web` (Gunicorn), `worker` (Celery), `db` (PostgreSQL), `redis`. Uploaded media lives in the `media_data` volume.

## Endpoints

### Authentication

```text
POST /api/accounts/register/
POST /api/token/                 {"email": ..., "password": ...}
POST /api/token/refresh/
POST /api/accounts/logout/       {"refresh": ...}   (blacklists the refresh token)
GET/PATCH /api/accounts/me/
```

### Catalog

```text
GET    /api/catalog/products/            ?category__slug= ?search= ?ordering=-price ?page= ?page_size=
GET    /api/catalog/products/{slug}/
POST   /api/catalog/products/{slug}/images/   (staff, multipart: image, alt_text, is_primary)
GET    /api/catalog/categories/
```

Product and category writes (POST/PUT/PATCH/DELETE) are staff-only. Deleting something that is still referenced returns 409; deactivate it instead.

### Cart

```text
GET    /api/cart/
POST   /api/cart/items/          {"product_id": 1, "quantity": 2}
PATCH  /api/cart/items/{id}/     {"quantity": 3}
DELETE /api/cart/items/{id}/
```

### Orders

```text
POST /api/orders/checkout/       {"shipping_name": ..., "shipping_phone": ..., "shipping_address": ...}
GET  /api/orders/
GET  /api/orders/{id}/
POST /api/orders/{id}/cancel/    (unpaid, pending orders only)
```

Orders of at least 100.00 ship free; otherwise shipping is 9.99.

### Payments

```text
POST /api/payments/mock/         {"order_id": 1}
```

## Maintenance commands

```bash
python manage.py seed_demo               # demo catalog
python manage.py expire_pending_orders   # cancel stale unpaid orders (--hours N); schedule via cron/Celery beat
```

## Testing and linting

```bash
pytest                           # in-memory SQLite, eager Celery, locmem email
TEST_USE_POSTGRES=1 pytest       # against the PostgreSQL from your .env (what CI does)
ruff check .
```

SQLite ignores `select_for_update`, so row-locking behaviour is only truly exercised on PostgreSQL.

## Configuration

All configuration is via environment variables; see `.env.example`. With `DEBUG=0` a real `SECRET_KEY` is mandatory and HTTPS-related security settings switch on. Before deploying run:

```bash
python manage.py check --deploy
```

## Before real production use

This is an educational production-style backend, not a complete marketplace. Add a real payment gateway (implement `PaymentGateway` and verify/deduplicate webhooks), object storage for media (WhiteNoise serves static files only), a real email provider, a reverse proxy with HTTPS, centralized logging/monitoring, backups, and schedule `expire_pending_orders`.
