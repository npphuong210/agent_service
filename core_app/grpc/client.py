import grpc
import os
from pb import ocr_service_pb2, ocr_service_pb2_grpc, stt_service_pb2_grpc, stt_service_pb2, face_recognition_pb2, face_recognition_pb2_grpc

def read_file_as_bytes(file_path):
    with open(file_path, 'rb') as f:
        file_content = f.read()  # Read the file as bytes
    return file_content
            
def get_file(stub):

    file = read_file_as_bytes("core_app/grpc/data/image copy 8.png")
    name = '2.png'
    
    request = ocr_service_pb2.FileRequest(
        file_name = name,
        file = file,
    )
    a = stub.CreateTextFromFile(request)
    print(a)
    
    
def upload_file(stub, file_path):
    def file_chunks():
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(1024*32)  # Read in 1KB chunks
                if not chunk:
                    break
                print(f"Sending chunk of size: {len(chunk)}")
                #return iter([].append(ai_service_pb2.AudioChunk(chunk_data=chunk)))
                yield stt_service_pb2.AudioChunkRequest(chunk_data=chunk)
                
    try:
        response_iterator = stub.StreamAudio(file_chunks())
        for response in response_iterator:
            print(f"Received transcription: {response.transcription}")
    except grpc.RpcError as e:
        print(f"gRPC error: {e.code()} - {e.details()}")
        

def run_audio(stub, audio_file_path):    
    def read_audio_file(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file {file_path} not found.")
        with open(file_path, 'rb') as f:
            return f.read()
    try:
        audio_data = read_audio_file(audio_file_path)
        print("Sending UploadAudio request...")
        response = stub.UploadAudio(stt_service_pb2.AudioFileRequest(file_data=audio_data))
        print("Upload Audio Response:", response.transcription)
        return response
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except grpc.RpcError as e:
        print(f"Upload Audio RPC error: {e.code()} - {e.details()}")
    
def add_Face(stub, file_image):
    
    image = read_file_as_bytes(file_image)
    
    request = face_recognition_pb2.UploadImageRequest(
        file_data=image,
        Country="Vietnam",
        FullName="quang linh vlog",
        Birthday="1992-01-01",
        Gender="Male",
        Age="34",
        Email="nguyenvana@example.com",
        Phone_number="0123456789",
        subsystem="DemoHUB"
    )    
    
    # Gửi request và nhận response
    response = stub.UploadImage(request)
    
    # In ra thông báo từ server
    print(f"Response: {response.message}, Status Code: {response.status_code}")

def recognize_face(stub, file_image):
    
    image = read_file_as_bytes(file_image)
    
    response = stub.UploadImageRecognition(face_recognition_pb2.ImageRecognition(file_data=image))
    
    print(f"Response: {response.message}, Status Code: {response.status_code}")

def run():
    audio_file_path = "core_app/grpc/data/Why does JavaScript's fetch make me wait TWICE_.mp3"
    image_file_path = "core_app/grpc/data/hieupc.jpeg"
    
    with grpc.insecure_channel('localhost:50051') as channel:
        stub_ocr = ocr_service_pb2_grpc.OCRServiceStub(channel)
        stub_stt = stt_service_pb2_grpc.STTServiceStub(channel)
        stub_face = face_recognition_pb2_grpc.FaceRecognitionServiceStub(channel)
        
        get_file(stub_ocr)
        #upload_file(stub_stt, audio_file_path)
        #run_audio(stub_stt, audio_file_path)
        
        # add_Face(stub_face, image_file_path)
        #recognize_face(stub_face, image_file_path)

if __name__ == '__main__':
    run()
