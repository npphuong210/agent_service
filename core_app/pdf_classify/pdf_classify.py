import fitz  # PyMuPDF
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
from io import BytesIO

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def is_scanned_pdf(pdf_binary):
    # Create a file-like object from the binary data
    file_like_object = BytesIO(pdf_binary)

    # Try to extract text using pdfminer
    try:
        text = extract_text(file_like_object)
        if text.strip():
            return False  # Standard PDF with extractable text
    except Exception as e:
        print(f"Error using pdfminer to extract text: {e}")

    # If text extraction fails, use PyMuPDF to check for images and run OCR
    try:
        file_like_object.seek(0)  # Reset the pointer to the beginning of the file
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