import re
import pandas as pd
from pypdf import PdfReader


def validate_pdf(file_path):
    reader = PdfReader(str(file_path))
    results = []
    extracted_pages = []

    email_pattern = re.compile(
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
        re.I
    )

    phone_pattern = re.compile(
        r'(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)'
    )

    amount_pattern = re.compile(
        r'(?:₹|INR\s*|Rs\.?\s*)-?\s*\d[\d,]*(?:\.\d{1,2})?',
        re.I
    )

    id_pattern = re.compile(
        r'\b(Invoice\s*ID|Invoice\s*No\.?|Customer\s*ID|'
        r'Order\s*ID|Reference\s*ID)\s*[:#-]?\s*'
        r'([A-Z0-9][A-Z0-9/-]{2,})',
        re.I
    )

    valid_email = re.compile(
        r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$',
        re.I
    )

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text)

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

    columns = ["Page", "Type", "Value", "Status"]
    result_df = pd.DataFrame(results, columns=columns)

    return "\n".join(extracted_pages), result_df
