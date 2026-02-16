import pdfplumber

def extract(file_path: str):
    pages_out = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_out.append({
                "page_number": i,
                "text": text.strip()
            })

    return pages_out
