import os

environment = os.environ.get("DJANGO_SETTINGS_MODULE", "")

if not environment:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
