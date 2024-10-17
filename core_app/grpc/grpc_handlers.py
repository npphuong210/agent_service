import time
import grpc
from faster_whisper import WhisperModel
import pyaudio 
import numpy as np
import io
import os
from io import BytesIO
import torch  # Add this import
# grpc handlers
from concurrent import futures
from core_app.grpc.pb import ocr_service_pb2, ocr_service_pb2_grpc, stt_service_pb2, stt_service_pb2_grpc
from pdfminer.high_level import extract_text
from core_app.pdf_classify.pdf_classify import is_scanned_pdf, process_scanned_pdf_with_llm, get_image_informations
from PIL import Image
import logging

logging.basicConfig(filename='document_processing.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension

def whisper_model(model_size, device=None):
    if device is None:
        if torch.cuda.is_available():
            device = 'cuda'
            compute_type = 'float16'
        else:
            device = 'cpu'
            compute_type = 'int8' 

    model = WhisperModel(model_size_or_path=model_size, device=device, compute_type=compute_type)
    return model

def transcribe_audio(audio_stream, init_prompt=None):
    model = whisper_model(model_size='base')
    try:
        segments, info = model.transcribe(audio=audio_stream, initial_prompt=init_prompt, beam_size=3, word_timestamps=True, condition_on_previous_text=True)
        transcription = " ".join([segment.text for segment in segments])
        return transcription.strip()
    except Exception as e:
        return "Error during transcription"

class OCRServiceServicer(ocr_service_pb2_grpc.OCRServiceServicer):

    def CreateTextFromFile(self, request, context):
        try:
            file_name = request.file_name
            pdf = request.file
            text = None

            logger.info(f"Processing file: {file_name}")

            if is_scanned_pdf(pdf):
                # if scanned PDF => vision LLM model
                file_name = file_name.lower()
                if file_name.endswith('.pdf'):
                    logger.info("The file is a scanned PDF.")
                    text = process_scanned_pdf_with_llm(pdf)
                elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                    logger.info("The file is an image.")
                    image = Image.open(BytesIO(pdf))
                    text = get_image_informations(image)
                else:
                    logger.warning("Unsupported file format.")
                    return ocr_service_pb2.FileResponse(
                        message = "Unsupported file format",
                        text = ""
                        )
            else:
                logger.info("The file is a regular PDF with extractable text.")
                file_like_object = BytesIO(pdf)
                text = extract_text(file_like_object)

            if text.startswith("ERROR:"):
                if "too small" in text.lower() or "unclear" in text.lower():
                    logger.warning(f"Problem: {text}")
                    return ocr_service_pb2.FileResponse(
                        message = "error.image-too-small-or-unclear",
                        text = ""
                        )
                else:
                    logger.warning(f"Error during OCR processing: {text}")
                    return ocr_service_pb2.FileResponse(
                        message = "error.can-not-read-file",
                        text = text
                        )
                    
            logger.info(f"Successfully processed file: {file_name}")
            return ocr_service_pb2.FileResponse(
                message = "", 
                text = text
                )
        
        except Exception as e:
            logger.error(f"Error during OCR processing for file {file_name}: {e}")
            return ocr_service_pb2.FileResponse(
                message = "error.unknown-error",
                text = ""
                )

class STTServiceServicer(stt_service_pb2_grpc.STTServiceServicer):

    def UploadAudio(self, request, context):
        start_time = time.time()

        audio_data = io.BytesIO(request.file_data)

        logger.info("Starting audio transcription for uploaded file.")
        
        try:
            transcription = transcribe_audio(audio_data)
            logger.info("Successfully transcribed uploaded audio file.")
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}")
            return stt_service_pb2.TranscriptionResponse(transcription="Error during transcription")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"Total processing time for uploaded audio: {total_time:.2f} seconds")


        return stt_service_pb2.TranscriptionResponse(transcription=transcription)

    def StreamAudio(self, request_iterator, context):
        audio_stream = io.BytesIO()
        buffer_size = 1024  * 32# Example buffer size (10KB)
        buffer = bytearray()
        init_prompt = ""
        
        start_time = time.time()

        logger.info("Starting streaming audio transcription.")

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
                        init_prompt += transcription
                        init_prompt = init_prompt[-100:]
                        
                        logger.info(f"Transcribed chunk: {transcription}")

                        yield stt_service_pb2.TranscriptionStreamingResponse(transcription=transcription)
                    except Exception as e:
                        logger.error(f"Error during chunk transcription: {e}")
                        yield stt_service_pb2.TranscriptionStreamingResponse(transcription="Error during transcription")

                    # Clear the buffer for the next set of chunks
                    buffer.clear()

                    # Move the stream cursor to the end to prepare for more data
                    audio_stream.seek(0, io.SEEK_END)

            # Process any remaining data in the buffer after the stream ends
            if buffer:
                audio_stream.write(buffer)
                audio_stream.seek(0)
                try:
                    transcription = transcribe_audio(audio_stream, init_prompt)
                    logger.info(f"Final chunk transcription: {transcription}")
                    yield stt_service_pb2.TranscriptionStreamingResponse(transcription=transcription)
                except Exception as e:
                    logger.error(f"Error during final transcription: {e}")
                    yield stt_service_pb2.TranscriptionStreamingResponse(transcription="Error during transcription")

        except Exception as e:
            logger.error(f"Error during audio streaming: {e}")
            return "Error: during the streaming"
        finally:
            audio_stream.close()

        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Total processing time for audio streaming: {total_time:.2f} seconds")

