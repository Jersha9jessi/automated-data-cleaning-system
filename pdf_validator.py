import re
import io
import pandas as pd
from pypdf import PdfReader


def validate_pdf(file_path):
    reader = PdfReader(str(file_path))
    results = []
    extracted_pages = []

    email_pattern = re.compile(
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I
    )
    phone_pattern = re.compile(
        r'(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)'
    )
    amount_pattern = re.compile(
        r'(?:₹|INR\s*|Rs\.?\s*)-?\s*\d[\d,]*(?:\.\d{1,2})?', re.I
    )
    id_pattern = re.compile(
        r'\b(Invoice\s*ID|Invoice\s*No\.?|Customer\s*ID|'
        r'Order\s*ID|Reference\s*ID)\s*[:#-]?\s*'
        r'([A-Z0-9][A-Z0-9/-]{2,})', re.I
    )
    valid_email = re.compile(
        r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$', re.I
    )

    ocr_document = None

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        extraction_method = "Text Extraction"

        if not page_text.strip():
            if ocr_document is None:
                try:
                    import fitz
                    import pytesseract
                    from PIL import Image
                except ImportError as error:
                    raise RuntimeError(
                        "Scanned PDF OCR dependencies are missing. "
                        "Please deploy the app with PyMuPDF, pytesseract, "
                        "Pillow and Tesseract OCR installed."
                    ) from error

                ocr_document = fitz.open(str(file_path))

            try:
                import fitz
                import pytesseract
                from PIL import Image

                pdf_page = ocr_document[page_number - 1]
                pix = pdf_page.get_pixmap(matrix=fitz.Matrix(3, 3))
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                page_text = pytesseract.image_to_string(
                    image, lang="eng"
                )
                extraction_method = "OCR"
            except Exception as error:
                raise RuntimeError(
                    f"OCR failed on PDF page {page_number}: {error}"
                ) from error

        extracted_pages.append(
            f"[Page {page_number} - {extraction_method}]\n{page_text}"
        )

        for value in re.findall(r'\S+@\S+', page_text):
            value = value.strip(".,;:()[]{}<>\"'")
            status = (
                "Valid Format"
                if valid_email.fullmatch(value)
                else "Invalid Format"
            )
            results.append({
                "Page": page_number,
                "Type": "Email",
                "Value": value,
                "Status": status
            })

        for value in phone_pattern.findall(page_text):
            results.append({
                "Page": page_number,
                "Type": "Phone",
                "Value": value,
                "Status": "Valid Format"
            })

        for value in amount_pattern.findall(page_text):
            results.append({
                "Page": page_number,
                "Type": "Amount",
                "Value": value,
                "Status": "Detected - Verify Amount"
            })

        for label, value in id_pattern.findall(page_text):
            results.append({
                "Page": page_number,
                "Type": label,
                "Value": value,
                "Status": "Detected - Verify ID"
            })

    if ocr_document is not None:
        ocr_document.close()

    columns = ["Page", "Type", "Value", "Status"]
    result_df = pd.DataFrame(results, columns=columns)
    return "\n".join(extracted_pages), result_df
