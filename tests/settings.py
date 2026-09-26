SECRET_KEY = "querywatch-test-key"
INSTALLED_APPS = []
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
USE_TZ = True

