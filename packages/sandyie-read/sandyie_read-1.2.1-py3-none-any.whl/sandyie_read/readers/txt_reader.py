import os
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_txt(file_path: str, *args, **kwargs) -> str:
    """
    Reads a .txt or .log file and returns its content as a string.
    Accepts additional parameters for open() (e.g., encoding, errors).
    """
    try:
        if not os.path.exists(file_path):
            raise SandyieException(f"Text file not found: {file_path}")

        try:
            # Try with user-specified params, default to UTF-8
            encoding = kwargs.pop("encoding", "utf-8")
            errors = kwargs.pop("errors", "strict")

            with open(file_path, "r", encoding=encoding, errors=errors, *args, **kwargs) as file:
                content = file.read()
        except UnicodeDecodeError:
            # Fallback to utf-16 if utf-8 fails (only if user didn't override encoding)
            if encoding == "utf-8":
                with open(file_path, "r", encoding="utf-16", errors=errors, *args, **kwargs) as file:
                    content = file.read()
            else:
                raise

        logger.info(f"[TXTReader] Successfully read TXT file: {file_path}")
        return content

    except FileNotFoundError:
        logger.error(f"Text file not found: {file_path}")
        raise SandyieException(f"Text file not found: {file_path}")
    except Exception as e:
        logger.exception("Failed to read TXT file.")
        raise SandyieException(f"Failed to read TXT file: {file_path}. Error: {str(e)}")
