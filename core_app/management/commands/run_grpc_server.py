from django.core.management.base import BaseCommand
from core_app.grpc.grpc_server import serve
import os
import threading

class Command(BaseCommand):
    help = 'Starts the gRPC server and Django server'

    def handle(self, *args, **options):
        # Start gRPC server in a separate thread
        grpc_thread = threading.Thread(target=serve)
        grpc_thread.start()

        # Start Django development server
        os.system("python3 manage.py runserver")
