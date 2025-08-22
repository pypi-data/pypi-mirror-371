import os
import pandas as pd
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_json(path, *args, **kwargs):
    """
    Reads a JSON file and returns a pandas DataFrame.
    Assumes the JSON is either a list of records or a dict that can be normalized.
    """
    try:
        if not os.path.exists(path):
            raise SandyieException(f"JSON file not found: {path}")

        df = pd.read_json(path, *args, **kwargs)
        logger.info(f"[JSONReader] Successfully read JSON file: {path}")
        return df

    except ValueError as e:
        logger.error(f"[JSONReader] Malformed JSON file: {path} | Error: {e}")
        raise SandyieException("The JSON file is malformed or unsupported", e)

    except SandyieException:
        raise  # already handled above

    except Exception as e:
        logger.error(f"[JSONReader] Failed to read JSON file: {path} | Error: {e}")
        raise SandyieException("Failed to read the JSON file", e)
