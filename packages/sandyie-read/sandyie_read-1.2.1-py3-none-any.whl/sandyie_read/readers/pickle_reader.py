import pickle
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_pickle(path, *args, **kwargs):
    """
    Reads a .pickle or .pkl file and returns the deserialized Python object.
    Accepts extra parameters supported by pickle.load (e.g., encoding, fix_imports).
    """
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f, *args, **kwargs)
        logger.info(f"[PickleReader] Successfully read Pickle file: {path}")
        return obj
    except FileNotFoundError:
        logger.error(f"Pickle file not found: {path}")
        raise SandyieException(f"Pickle file not found: {path}")
    except Exception as e:
        logger.exception("Failed to read Pickle file.")
        raise SandyieException(f"Failed to read the .pickle/.pkl file: {str(e)}")
