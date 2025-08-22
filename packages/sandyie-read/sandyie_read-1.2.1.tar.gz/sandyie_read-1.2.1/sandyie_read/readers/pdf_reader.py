import fitz  # PyMuPDF
from sandyie_read.exceptions import SandyieException
import logging

logger = logging.getLogger(__name__)

def read_pdf(file_path: str, pages: list[int] = None, *args, **kwargs) -> str:
    """
    Reads the content from a PDF file with flexible options.

    Args:
        file_path (str): Path to the PDF file.
        pages (list[int], optional): Specific pages to read (0-based index).
        *args, **kwargs: Extra parameters forwarded to page.get_text()

    Returns:
        str: Extracted text/content from the PDF.

    Raises:
        SandyieException: If the PDF cannot be read.
    """
    try:
        logger.info(f"Reading PDF file: {file_path}")
        with fitz.open(file_path) as doc:
            results = []
            if pages is None:  # read all pages
                page_numbers = range(len(doc))
            else:  # only selected pages
                page_numbers = pages

            for i in page_numbers:
                page = doc[i]
                results.append(page.get_text(*args, **kwargs))
                
        return "\n".join(str(r) for r in results).strip()

    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise SandyieException(f"PDF file not found: {file_path}")
    except Exception as e:
        logger.exception("Failed to read PDF file.")
        raise SandyieException(f"Failed to read PDF file: {str(e)}")
