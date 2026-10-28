"""Settings used by pytest. Fast, isolated and independent of Redis/SMTP.

Set TEST_USE_POSTGRES=1 to run the suite against the PostgreSQL configured in the
environment (this is what CI does) instead of in-memory SQLite.
"""

import os

os.environ.setdefault("DEBUG", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from .settings import *  # noqa: E402,F401,F403
from .settings import REST_FRAMEWORK as _REST_FRAMEWORK  # noqa: E402

if os.getenv("TEST_USE_POSTGRES") != "1":
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    }

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
CELERY_TASK_ALWAYS_EAGER = True

REST_FRAMEWORK = {
    **_REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100000/min",
        "user": "100000/min",
        "auth": "100000/min",
    },
}
