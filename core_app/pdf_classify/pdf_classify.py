import fitz  # PyMuPDF
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
from io import BytesIO
from .vision_model import get_image_informations
import logging
logger = logging.getLogger(__name__)

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def is_scanned_pdf(pdf_binary):
    # Create a file-like object from the binary data
    file_like_object = BytesIO(pdf_binary)

    logger.info("Starting to check if PDF is scanned.")

    try:
        text = extract_text(file_like_object)
        if text.strip():
            logger.info("PDF contains extractable text, not a scanned PDF.")
            return False  # PDF chuẩn với văn bản có thể trích xuất
    except Exception as e:
        logger.error(f"Error using pdfminer: {e}")

    try:
        file_like_object.seek(0)
        pdf_document = fitz.open("pdf", file_like_object)
        logger.info("Successfully opened PDF with PyMuPDF.")

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            text = pytesseract.image_to_string(img)
            if text.strip():
                logger.info(f"Page {page_num} contains text, scanned PDF detected.")
                return True  # Scanned PDF with text from OCR
    except Exception as e:
        logger.error(f"Error using PyMuPDF and Tesseract OCR {e}")

    logger.warning("No text found, assuming this is a scanned PDF.")
    return True  # Assume it's scanned if no text found



def process_scanned_pdf_with_llm(pdf_binary, lang_key):
    """
    Process a scanned PDF using the Vision LLM model.

    :param pdf_binary: The binary data of the scanned PDF.
    :return: Processed result from the Vision LLM model.
    """

    logger.info("Starting to process scanned PDF with Vision LLM model.")
    # Convert the binary PDF to images (one image per page)
    file_like_object = BytesIO(pdf_binary)
    pdf_document = fitz.open("pdf", file_like_object)
    results = []

    logger.info(f"PDF contains {len(pdf_document)} pages.")

    for page_num in range(len(pdf_document)):
        try:
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)

            logger.info(f"Page {page_num} contains {len(image_list)} images.")

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                img = Image.open(BytesIO(image_bytes))

                logger.info(f"Processing image {img_index + 1} on page {page_num}.")
        
                # Process the image using the get_image_informations function
                result = get_image_informations(img, lang_key)
                # result = pytesseract.image_to_string(img)

                results.append(result)

                logger.info(f"Successfully processed image {img_index + 1} on page {page_num}.")
        
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {e}")

    combined_result = "\n".join(results)

    logger.info("Completed processing scanned PDF with Vision LLM model.")

    return combined_result