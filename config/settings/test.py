from .base import *


SECRET_KEY = env("DJANGO_SECRET_KEY")

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

MEDIA_URL = "http://media.testserver/"

ALLOWED_HOSTS = ["localhost", ".localhost", "0.0.0.0", "127.0.0.1"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
        }
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}