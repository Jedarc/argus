import os

# Must be set before any api.* import to satisfy module-level os.environ reads.
os.environ.setdefault("JWT_SECRET_KEY", "pytest-test-secret-key-minimum-32-chars!")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
