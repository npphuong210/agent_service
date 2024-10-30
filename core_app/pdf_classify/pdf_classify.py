import fitz  # PyMuPDF
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
from io import BytesIO
from .vision_model import get_image_informations, support_informations_LLM
from langdetect import detect, detect_langs
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



def process_scanned_pdf_with_llm(pdf_binary):
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
                try:
                    text = pytesseract.image_to_string(img, lang='vie+eng+jpn+kor')

                    logger.info("Extracted text using Tesseract.")
                    # Detect multiple languages in the extracted text
                    detected_langs = detect_langs(text)

                    logger.info(f"Detected languages: {detected_langs}")

                    # Check if language > 0.9
                    detected_langs = [lang for lang in detected_langs if lang.prob > 0.9]   

                    # Combine detected languages into a single string
                    detected_langs_str = '+'.join([lang.lang for lang in detected_langs])
                    logger.info(f"Detected languages: {detected_langs_str}")
                    
                    if detected_langs:
                        # Language map for Tesseract
                        tesseract_lang_map = {
                            'vi': 'vie',  # Vietnamese
                            'en': 'eng',  # English
                            'ja': 'jpn',  # Japanese
                            'ko': 'kor',  # Korean
                            'fr': 'fra',  # French
                            'es': 'spa',  # Spanish
                            'de': 'deu',  # German
                            'ru': 'rus',  # Russian
                            # Add other languages as needed
                        }

                        # Convert detected languages to Tesseract format
                        tesseract_langs = '+'.join([tesseract_lang_map[lang.lang] for lang in detected_langs if lang.lang in tesseract_lang_map])
                        logger.info(f"Tesseract languages: {tesseract_langs}")

                        if tesseract_langs:
                            logger.info(f"Using Tesseract with languages: {tesseract_langs}")
                            text = pytesseract.image_to_string(img, lang=tesseract_langs)
                            logger.info("Text improved using Tesseract.")
                            try:
                                text = support_informations_LLM(text, img)
                                logger.info("Text improved using support_informations_LLM.")
                            except Exception as e:
                                logger.error(f"Error processing text with Vision LLM model: {e}")
                    else:
                        logger.info("No languages detected, using Tesseract with default languages.")
                        try:
                            logger.info("Text extracted using Vision LLM model.")
                            text = get_image_informations(img)
                        except Exception as e:
                            logger.error(f"Error during get_image_informations: {e}")
                        
                except Exception as e:
                    logger.info("Using LLM for image text extraction (get_image_informations).")
                    try:
                        text = get_image_informations(img)
                        logger.info("Text extracted using Vision LLM model.")
                    except Exception as llm_error:
                        logger.error(f"LLM extraction also failed: {llm_error}")
                        text = ""

                results.append(text)

                logger.info(f"Successfully processed image {img_index + 1} on page {page_num}.")
        
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {e}")

    combined_result = "\n".join(results)

    logger.info("Completed processing scanned PDF with Vision LLM model.")

    return combined_result