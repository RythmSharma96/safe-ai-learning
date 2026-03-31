from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database comes from DATABASE_URL env var (set in docker-compose)
# Falls back to Postgres on localhost if DATABASE_URL is not set
