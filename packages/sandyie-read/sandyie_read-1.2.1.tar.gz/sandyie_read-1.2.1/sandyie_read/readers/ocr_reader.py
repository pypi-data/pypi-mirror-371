from PIL import Image
import pytesseract
from sandyie_read.logging_config import logger

def read_ocr(file_path, *args, **kwargs):
    """Extract text from image using OCR."""
    try:
        img = Image.open(file_path, *args, **kwargs)
        text = pytesseract.image_to_string(img)
        logger.info("Text extracted successfully using OCR.")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text using OCR: {e}")
        return None
