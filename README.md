# Django Authentication API

A Django REST Framework project providing JWT-based authentication, user registration, account activation, and profile management through a versioned REST API.

## Stack

- Python 3.12
- Django 5.2
- Django REST Framework
- Simple JWT with refresh-token rotation and blacklisting
- PostgreSQL
- Redis for caching and request throttling
- Celery for asynchronous task processing
- drf-yasg / Swagger UI
- drf-spectacular / OpenAPI schema generation
- Docker Compose
- Gunicorn and WhiteNoise
- pytest + pytest-django
- Ruff

## Project Layout

```text
apps/
└── accounts/
    ├── api/
    │   └── v1/
    │       ├── serializer.py
    │       ├── urls.py
    │       └── views.py
    ├── migrations/
    ├── models.py
    ├── admin.py
    ├── apps.py
    ├── urls.py
    └── views.py

config/
├── settings.py
├── urls.py
├── views.py
├── celery.py
├── pagination.py
├── asgi.py
└── wsgi.py

tests/
├── conftest.py
├── test_accounts.py
└── test_health.py

nginx/
Dockerfile
compose.yaml
manage.py
pytest.ini
requirements.txt
ruff.toml
architecture.md
```

## Features

### Authentication

- User registration with email and password validation
- Email normalization and case-insensitive duplicate-email checks
- JWT access and refresh token generation
- Access token verification
- Refresh token rotation and blacklisting
- Authenticated logout with refresh-token invalidation
- Authentication endpoint throttling

### User Management

- Custom user model based on Django's `AbstractUser`
- Email-based authentication instead of username
- Unique email addresses
- Account activation through a token-based endpoint
- Authenticated password change with current-password verification
- Retrieve and update the authenticated user's profile
- Read-only email and user ID fields in profile updates

### Security

- Django password validation
- JWT-based authentication
- Permission-controlled API endpoints
- Scoped throttling for authentication operations
- Environment-based configuration
- Production-oriented HTTPS and secure-cookie settings
- Configurable database and cache backends

## API Endpoints

The following endpoints are based on the current URL configuration.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/token/create/` | Obtain access and refresh tokens |
| POST | `/token/refresh/` | Refresh an access token |
| POST | `/token/logout/` | Blacklist a refresh token |
| POST | `/accounts/api/v1/registration/` | Register a new user |
| GET | `/accounts/api/v1/jwt/verify/` | Verify a JWT token |
| GET | `/accounts/api/v1/activation/confirm/<token>` | Activate a user account |

### Profile & Password Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/accounts/api/v1/profile/` | Retrieve the authenticated user's profile |
| PUT | `/accounts/api/v1/profile/` | Update supported profile fields |
| PATCH | `/accounts/api/v1/profile/` | Partially update the profile |
| PUT | `/accounts/api/v1/change_password/` | Change the current user's password |

### Health Check & Documentation

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/` | Health check |
| GET | `/swagger/` | Interactive Swagger UI |
| GET | `/admin/` | Django administration |

## Example Requests

### Register a User

```http
POST /accounts/api/v1/registration/
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "StrongPass123!",
  "password2": "StrongPass123!"
}
```

A successful registration returns `201 Created`.

The registration serializer normalizes email addresses to lowercase, checks for duplicate addresses without case sensitivity, and applies Django's configured password validators.

### Obtain JWT Tokens

```http
POST /token/create/
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

A successful response provides an access token and a refresh token.

### Authenticate API Requests

Include the access token in the `Authorization` header:

```http
Authorization: Bearer <access-token>
```

### Logout

```http
POST /token/logout/
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "refresh": "<refresh-token>"
}
```

A successful logout returns `204 No Content` and blacklists the refresh token. The endpoint also checks that the refresh token belongs to the authenticated user.

## JWT Configuration

The current configuration specifies:

- Access token lifetime: 30 minutes
- Refresh token lifetime: 7 days
- Refresh token rotation enabled
- Blacklisting after refresh-token rotation enabled
- Last-login updates enabled

## Local Setup

### Prerequisites

- Python 3.12
- Git
- PostgreSQL, unless using SQLite
- Redis when using Redis-backed caching or Celery

### 1. Clone the Repository

```bash
git clone <repository-url>
cd django-auth-api
```

Replace `<repository-url>` with the actual repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the required environment variables.

Example for local development with PostgreSQL:

```dotenv
DEBUG=True
SECRET_KEY=replace-with-a-local-development-secret
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=marketplace
POSTGRES_USER=marketplace
POSTGRES_PASSWORD=replace-with-a-local-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

USE_SQLITE=False
REDIS_URL=redis://localhost:6379/0
CACHE_URL=redis://localhost:6379/1
```

Use real, unique secrets in any shared or production environment. Never commit the actual `.env` file.

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create an Administrator

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at:

- API base: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- Admin: `http://127.0.0.1:8000/admin/`
- Health check: `http://127.0.0.1:8000/health/`

## Docker

The project includes a Dockerfile and Docker Compose configuration for running the application with PostgreSQL and Redis.

Create the environment file, then start the services:

```bash
docker compose up --build
```

The Compose configuration starts:

- `web` — Django development server
- `worker` — Celery worker
- `db` — PostgreSQL
- `redis` — Redis

The web service applies database migrations when it starts.

Create an administrator account:

```bash
docker compose exec web python manage.py createsuperuser
```

Stop the services:

```bash
docker compose down
```

Named volumes preserve PostgreSQL data, Redis data, and uploaded media between container restarts.

**Note:** The current Compose configuration uses Django's development server. The Dockerfile defines Gunicorn, but the Compose web command overrides the image's default command. Production deployment requires a separate, production-appropriate configuration.

## Testing

The project uses pytest and pytest-django for automated testing.

Run the test suite locally:

```bash
pytest
```

Or run it inside the Docker web container:

```bash
docker compose exec web pytest
```

The current test suite covers:

- Rejecting weak passwords
- Rejecting duplicate email addresses regardless of letter case
- Normalizing email addresses
- Requiring authentication for profile access
- Preventing profile email changes
- Blacklisting refresh tokens on logout
- Rejecting invalid refresh tokens during logout
- Verifying public health endpoint behavior

## Configuration & Security Notes

- `DEBUG` defaults to `False`.
- A valid `SECRET_KEY` is required when debug mode is disabled.
- PostgreSQL is the default database; SQLite can be enabled with `USE_SQLITE`.
- Redis can provide a shared cache for throttling counters across application workers.
- Authentication endpoints use a dedicated throttle scope.
- HTTPS-related security settings are enabled when debug mode is disabled, subject to the relevant configuration.
- Refresh-token blacklisting requires the Simple JWT token blacklist application and its database migrations.

Before deploying, review the environment variables, database configuration, HTTPS setup, and security settings for the target environment.

## Project Status

This project is under active development and focuses on authentication, user management, API security, and automated testing.

## License

No license has been specified yet.
