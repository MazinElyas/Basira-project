
"""engines.py

OCR engine wrappers for Tesseract and GCP OCR.

The goal is to demonstrate:
- Clear separation of OCR engines
- Realistic integration points for Tesseract and GCP Vision/Document AI
- Simple, readable timing and status reporting
"""

from __future__ import annotations

import time
from typing import Any, Dict

# Real-world imports (kept commented so the file is self-contained

# import pytesseract
# from PIL import Image
# from google.cloud import vision


def run_tesseract(file_path: str) -> Dict[str, Any]:
    """Run OCR using Tesseract (open source).

    In a production environment, this function would typically:
      - Open the image/PDF
      - Convert it to a Tesseract-friendly format
      - Call pytesseract.image_to_string(...)
      - Return the extracted text and timing metadata
    """
    start = time.time()

    # Example of how real code would look:
    #
    # img = Image.open(file_path)
    # extracted_text = pytesseract.image_to_string(img, lang="eng")
  
    simulated_text = f"[Tesseract] Simulated OCR text from: {file_path}"

    runtime = time.time() - start

    return {
        "text": simulated_text,
        "runtime": runtime,
        "status": "success",
        "engine": "tesseract",
    }


def run_gcp_ocr(file_path: str) -> Dict[str, Any]:
    """Run OCR using GCP Vision / Document AI.

    In a production environment, this function would typically:
      - Instantiate a Google Cloud Vision or Document AI client
      - Read the file content as bytes
      - Send a document_text_detection or process_document request
      - Extract full text from the response
      - Return the extracted text and timing metadata
    """
    start = time.time()

    # Example of how real code would look:
    #
    # client = vision.ImageAnnotatorClient()
    # with open(file_path, "rb") as f:
    #     content = f.read()
    # image = vision.Image(content=content)
    # response = client.document_text_detection(image=image)
    # extracted_text = response.full_text_annotation.text

    simulated_text = f"[GCP OCR] Simulated OCR text from: {file_path}"

    # Simulate slightly higher latency than Tesseract
    time.sleep(0.2)
    runtime = time.time() - start

    return {
        "text": simulated_text,
        "runtime": runtime,
        "status": "success",
        "engine": "gcp_ocr",
    }
