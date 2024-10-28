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
     
    #     # Log the environment variable to verify its value
    #     run_main = os.environ.get('RUN_MAIN')
    #     #print(f'RUN_MAIN: {run_main}')  # Log the value of RUN_MAIN

    #     # Only add crontab jobs if running the server
    #     if run_main == 'true':
    #         print("Adding crontab jobs...")
    #         call_command('crontab', 'add')
    #         # Register shutdown event to remove crontab jobs
    #         atexit.register(self.remove_cron_jobs)
    #     else:
    #         print("Not adding crontab jobs. RUN_MAIN is not 'true'.")

    # def remove_cron_jobs(self):
    #     print('Removing crontab jobs...')
    #     call_command('crontab', 'remove')