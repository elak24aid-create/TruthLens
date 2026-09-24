import asyncio
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extracts text from an image using Windows native OCR (WinRT).
    Saves the image temporarily to disk as WinRT StorageFile requires a file path.
    """
    try:
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.graphics.imaging import BitmapDecoder
        from winrt.windows.storage import StorageFile
        from winrt.windows.globalization import Language
    except ImportError:
        logger.error("winrt OCR packages are not installed.")
        raise Exception("OCR engine is not available on this system.")

    if not OcrEngine.is_language_supported(Language("en-US")):
        raise Exception("English language is not supported by the local OCR engine.")

    engine = OcrEngine.try_create_from_language(Language("en-US"))
    
    # Safely create a temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
    try:
        with os.fdopen(temp_fd, 'wb') as f:
            f.write(image_bytes)
        
        file = await StorageFile.get_file_from_path_async(os.path.abspath(temp_path))
        stream = await file.open_read_async()
        
        decoder = await BitmapDecoder.create_async(stream)
        software_bitmap = await decoder.get_software_bitmap_async()
        
        result = await engine.recognize_async(software_bitmap)
        
        return result.text
        
    except Exception as e:
        logger.error(f"Error during OCR extraction: {e}")
        raise Exception(f"Failed to extract text from image: {e}")
    finally:
        # Ensure temporary file is always cleaned up
        try:
            os.remove(temp_path)
        except OSError:
            pass
