import grpc
from concurrent import futures

# Import generated gRPC modules
from core_app.grpc.pb.ocr_service_pb2_grpc import add_OCRServiceServicer_to_server
from core_app.grpc.pb.stt_service_pb2_grpc import add_STTServiceServicer_to_server


# Import your service implementations
from .grpc_handlers import (
    OCRServiceServicer,
    STTServiceServicer
)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register services
    add_OCRServiceServicer_to_server(OCRServiceServicer(), server)
    add_STTServiceServicer_to_server(STTServiceServicer(), server)

    
    # Start the server
    server.add_insecure_port('0.0.0.0:6443')
    server.start()
    server.wait_for_termination()
