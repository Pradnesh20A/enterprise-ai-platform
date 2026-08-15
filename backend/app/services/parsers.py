import io
from typing import Optional

import fitz  # PyMuPDF


async def parse_document(file_content: bytes, file_type: str) -> Optional[str]:
    """Extract text from supported file types.
    
    Args:
        file_content: The raw bytes of the file.
        file_type: The extension/type of the file (e.g., 'pdf', 'txt').
        
    Returns:
        The extracted text as a single string, or None if extraction fails or format is unsupported.
    """
    file_type = file_type.lower()
    
    if file_type == 'txt':
        return _parse_txt(file_content)
    elif file_type == 'pdf':
        return _parse_pdf(file_content)
    else:
        # We can add more parsers (docx, etc.) here later.
        # Images (jpg, png) would require OCR (e.g., Tesseract), which is out of scope for now.
        return None

def _parse_txt(file_content: bytes) -> Optional[str]:
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback to a common encoding if utf-8 fails
            return file_content.decode('latin-1')
        except Exception:
            return None

def _parse_pdf(file_content: bytes) -> Optional[str]:
    try:
        # Open the PDF from memory
        doc = fitz.open(stream=file_content, filetype="pdf")
        text_pages = []
        for page in doc:
            text_pages.append(page.get_text())
        doc.close()
        return "\n".join(text_pages)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None
