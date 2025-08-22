import io
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_svg(path, *args, **kwargs):
    """
    Reads an .svg file and returns its raw XML (as a string).
    Accepts additional parameters for io.open (e.g., encoding, errors).
    """
    try:
        with io.open(path, mode="r", *args, **kwargs) as f:
            content = f.read()
        logger.info(f"[SVGReader] Successfully read SVG file: {path}")
        return content
    except FileNotFoundError:
        logger.error(f"SVG file not found: {path}")
        raise SandyieException(f"SVG file not found: {path}")
    except Exception as e:
        logger.exception("Failed to read SVG file.")
        raise SandyieException(f"Failed to read the .svg file: {str(e)}")
