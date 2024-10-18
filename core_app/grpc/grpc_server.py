import grpc
from concurrent import futures

# Import generated gRPC modules
from core_app.grpc.pb.face_recognition_pb2_grpc import add_FaceRecognitionServiceServicer_to_server
from core_app.grpc.pb.ocr_service_pb2_grpc import add_OCRServiceServicer_to_server
from core_app.grpc.pb.stt_service_pb2_grpc import add_STTServiceServicer_to_server


# Import your service implementations
from .grpc_handlers import (
    OCRServiceServicer,
    STTServiceServicer,
    FaceRecognitionService
)

def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register services
    add_OCRServiceServicer_to_server(OCRServiceServicer(), server)
    add_STTServiceServicer_to_server(STTServiceServicer(), server)
    add_FaceRecognitionServiceServicer_to_server(FaceRecognitionService(), server)
    
    # Start the server
    server.add_insecure_port(f'0.0.0.0:{port}')
    print(f'gRPC server started on port {port}')
    server.start()
    server.wait_for_termination()
