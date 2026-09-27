import asyncio
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

async def extract_text_from_image(image_bytes: bytes) -> tuple[str, str]:
    """
    Extracts text from an image using pytesseract.
    Returns a tuple: (extracted_text, ocr_status)
    ocr_status can be: "OCR_SUCCESS", "OCR_UNAVAILABLE", "NO_TEXT_DETECTED"
    """
    try:
        import pytesseract
    except ImportError:
        logger.error("pytesseract package is not installed.")
        return ("", "OCR_UNAVAILABLE")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Ensure image is in a format tesseract can handle, though PIL usually handles it
        image.load()

        # Run OCR in a thread pool to avoid blocking the async event loop
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(None, pytesseract.image_to_string, image)
        
        text = text.strip() if text else ""
        
        if text:
            return (text, "OCR_SUCCESS")
        else:
            return ("", "NO_TEXT_DETECTED")
            
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract binary not found on the system. Please install tesseract-ocr.")
        return ("", "OCR_UNAVAILABLE")
    except Exception as e:
        logger.error(f"Error during OCR extraction: {e}")
        return ("", "OCR_UNAVAILABLE")
