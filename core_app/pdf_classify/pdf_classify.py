import fitz  # PyMuPDF
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
from io import BytesIO
from .vision_model import get_image_informations  # Import the VisionLLMModel


# Instantiate the model
# vision_llm_model = VisionLLMModel()

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def is_scanned_pdf(pdf_binary):
    # Create a file-like object from the binary data
    file_like_object = BytesIO(pdf_binary)

    try:
        text = extract_text(file_like_object)
        if text.strip():
            return False  # PDF chuẩn với văn bản có thể trích xuất
    except Exception as e:
        print(f"Error using pdfminer to extract text: {e}")

    try:
        file_like_object.seek(0)
        pdf_document = fitz.open("pdf", file_like_object)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            text = pytesseract.image_to_string(img)
            if text.strip():
                return True  # Scanned PDF with text from OCR
    except Exception as e:
        print(f"Error using PyMuPDF or Tesseract: {e}")


    return True  # Assume it's scanned if no text found



def process_scanned_pdf_with_llm(pdf_binary):
    """
    Process a scanned PDF using the Vision LLM model.

    :param pdf_binary: The binary data of the scanned PDF.
    :return: Processed result from the Vision LLM model.
    """
    # Convert the binary PDF to images (one image per page)
    file_like_object = BytesIO(pdf_binary)
    pdf_document = fitz.open("pdf", file_like_object)
    results = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            img = Image.open(BytesIO(image_bytes))
    
            # Process the image using the get_image_informations function
            result = get_image_informations(img)
            results.append(result)
    
    combined_result = "\n".join(results)
    
    return combined_result