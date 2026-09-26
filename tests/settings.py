SECRET_KEY = "querywatch-test-key"
INSTALLED_APPS = ["tests.testapp"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "analytics": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
MIGRATION_MODULES = {"testapp": None}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
