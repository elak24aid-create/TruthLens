import asyncio
import os
import sys

async def test_ocr(image_path):
    try:
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.graphics.imaging import BitmapDecoder
        from winrt.windows.storage import StorageFile
        from winrt.windows.globalization import Language

        # Check if OCR is supported
        if not OcrEngine.is_language_supported(Language("en-US")):
            print("en-US language not supported by OCR.")
            return

        engine = OcrEngine.try_create_from_language(Language("en-US"))
        
        file = await StorageFile.get_file_from_path_async(os.path.abspath(image_path))
        stream = await file.open_read_async()
        
        decoder = await BitmapDecoder.create_async(stream)
        software_bitmap = await decoder.get_software_bitmap_async()
        
        result = await engine.recognize_async(software_bitmap)
        
        print("OCR Text:", result.text)
        
    except Exception as e:
        print("Error during OCR:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(test_ocr(sys.argv[1]))
    else:
        print("No image path provided.")
