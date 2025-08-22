import logging
import os
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_js(path, *args, **kwargs):
    """
    Reads a .js (JavaScript) file and returns its content as plain text.
    Useful for viewing or analyzing raw JS code.
    """
    try:
        if not os.path.exists(path):
            raise SandyieException(f"JavaScript file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        logger.info(f"[JSReader] Successfully read JS file: {path}")
        return content

    except UnicodeDecodeError as e:
        logger.error(f"[JSReader] Unicode decode error in file: {path}")
        raise SandyieException("Could not decode the JavaScript file", e)
    except SandyieException:
        raise  # re-raise custom exception directly
    except Exception as e:
        logger.error(f"[JSReader] Unexpected error reading file: {path}, Error: {e}")
        raise SandyieException("Failed to read the JavaScript file", e)
