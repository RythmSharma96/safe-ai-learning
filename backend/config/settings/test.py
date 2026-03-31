from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use mock AI adapter in tests
AI_ADAPTER = "mock"

# Disable OpenAI moderation in tests (use keyword checker only)
SAFETY_USE_OPENAI_MODERATION = False

# Faster password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
