import grpc
import uuid
from pb import ocr_service_pb2
from pb import ocr_service_pb2_grpc

from google.protobuf.timestamp_pb2 import Timestamp

def read_file_as_bytes(file_path):
    with open(file_path, 'rb') as f:
        file_content = f.read()  # Read the file as bytes
    return file_content
            
def get_file(stub):

    file = read_file_as_bytes("core_app/grpc/data/1.pdf")
    name = '1.pdf'
    
    request = ocr_service_pb2.FileRequest(
        file_name = name,
        file = file
    )
    a = stub.CreateTextFromFile(request)
    print(a)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = ocr_service_pb2_grpc.OCRSserviceStub(channel)
        get_file(stub)
    


if __name__ == '__main__':
    run()
