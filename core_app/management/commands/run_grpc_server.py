from django.core.management.base import BaseCommand
from core_app.grpc.grpc_server import serve
import os
import threading


class Command(BaseCommand):
    help = 'Starts the gRPC server'
    
    def add_arguments(self, parser):
        
        #Optional port argument (default to 50051 if not provided)
        
        parser.add_argument(
            'port', type=int, nargs='?', default=50051,
            help='Port number to run the gRPC server on (default:50051)'
        )

    def handle(self, *args, **options):
        port = options['port']
        self.stdout.write(self.style.SUCCESS(f'Starting gRPC server on port {port}'))
        
        serve(port=port)


# class Command(BaseCommand):
#     help = 'Starts the gRPC server and Django server'

#     def handle(self, *args, **options):
#         # Start gRPC server in a separate thread
#         grpc_thread = threading.Thread(target=serve)
#         grpc_thread.start()

#         # Start Django development server
#         #os.system("python3 manage.py runserver")
