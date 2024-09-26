import grpc
from faster_whisper import WhisperModel
import pyaudio 
import numpy as np
import io
import os
from io import BytesIO
# grpc handlers
from concurrent import futures
from core_app.grpc.pb import ocr_service_pb2, ocr_service_pb2_grpc, stt_service_pb2, stt_service_pb2_grpc
from pdfminer.high_level import extract_text
from core_app.pdf_classify.pdf_classify import is_scanned_pdf, process_scanned_pdf_with_llm, get_image_informations
from PIL import Image

def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension

def whisper_model(model_size, device='cpu'):
    model = WhisperModel(model_size, device=device, compute_type="int8")
    return model

def transcribe_audio(audio_stream, init_prompt=None):
    model = whisper_model(model_size='tiny', device='cpu')
    try:
        segments, info = model.transcribe(audio=audio_stream, initial_prompt=init_prompt, beam_size=5, word_timestamps=True, condition_on_previous_text=True)
        transcription = " ".join([segment.text for segment in segments])
        return transcription.strip()
    except Exception as e:
        return "Error during transcription"

class OCRSserviceServicer(ocr_service_pb2_grpc.OCRSserviceServicer):

    def CreateTextFromFile(self, request, context):

        file_name = request.file_name
        pdf = request.file
        text = None
        print(file_name)
        #text = extract_text(file)

        if is_scanned_pdf(pdf):
            # if scanned PDF => vision LLM model
            file_name = file_name.lower()
            if file_name.endswith('.pdf'):
                print("Đây là PDF được scan.")
                text = process_scanned_pdf_with_llm(pdf)
            elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                print("Đây là hình ảnh.")
                image = Image.open(BytesIO(pdf))
                text = get_image_informations(image)
            else:
                print("Định dạng tệp không được hỗ trợ.")
                return None
        
        else:

            file_like_object = BytesIO(pdf)
            text = extract_text(file_like_object)

        return ocr_service_pb2.FileResponse(id=text)
    
class STTServiceServicer(stt_service_pb2_grpc.STTServiceServicer):

    def UploadAudio(self, request, context):
        audio_data = io.BytesIO(request.file_data)
        result = transcribe_audio(audio_data)
        return stt_service_pb2.TranscriptionResponse(transcription=result)

    def StreamAudio(self, request_iterator, context):
        audio_stream = io.BytesIO()
        buffer_size = 1024  * 10# Example buffer size (10KB)
        buffer = bytearray()
        init_prompt = None
        
        try:
            for chunk in request_iterator:
                if not chunk.chunk_data:
                    continue
                
                buffer.extend(chunk.chunk_data)
                

                # If the buffer reaches the defined size, process it
                if len(buffer) >= buffer_size:
                    audio_stream.write(buffer)
                    audio_stream.seek(0)

                    try:
                        transcription = transcribe_audio(audio_stream, init_prompt)
                        init_prompt = transcription[:200]
                        print('init_prompt: ', init_prompt)
                        print('chunk:', transcription)
                        yield stt_service_pb2.TranscriptionStreamingResponse(transcription=transcription)
                    except Exception as e:
                        yield stt_service_pb2.TranscriptionStreamingResponse(transcription="Error during transcription")

                    #offset = -1024 * 2 # Example: move 2KB back for context
                    #audio_stream.seek(offset, io.SEEK_CUR)

                    # Clear the buffer for the next set of chunks
                    buffer.clear()

                    # Move the stream cursor to the end to prepare for more data
                    audio_stream.seek(0, io.SEEK_END)
                    
                    
                    # # Clear the buffer and continue
                    # buffer.clear()
                    # audio_stream.seek(0, io.SEEK_END)

            # Process any remaining data in the buffer after the stream ends
            if buffer:
                audio_stream.write(buffer)
                audio_stream.seek(0)
                try:
                    transcription = transcribe_audio(audio_stream, init_prompt)
                    print('chunk:', transcription)
                    yield stt_service_pb2.TranscriptionStreamingResponse(transcription=transcription)
                except Exception as e:
                    yield stt_service_pb2.TranscriptionStreamingResponse(transcription="Error during transcription")

        except Exception as e:
            return "Error: during the streaming"
        finally:
            audio_stream.close()


