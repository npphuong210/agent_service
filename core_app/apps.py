from django.apps import AppConfig
from django.core.management import call_command
import atexit
import os

class CoreAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_app"

    def ready(self):
        import core_app.signals  # Import module signals
        print("Signals connected")