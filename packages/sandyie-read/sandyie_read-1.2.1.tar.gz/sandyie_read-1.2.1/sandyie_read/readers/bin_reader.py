import logging
import os
import base64
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_bin(path, as_base64: bool = False, as_hex: bool = False):
    """
    Reads a .bin file and returns its content.

    Parameters
    ----------
    path : str
        Path to the .bin file.
    as_base64 : bool, optional (default=False)
        If True, returns the content as a Base64-encoded string.
    as_hex : bool, optional (default=False)
        If True, returns the content as a hexadecimal string.

    Returns
    -------
    bytes | str
        - Raw bytes if both `as_base64` and `as_hex` are False (default).
        - Base64 string if `as_base64=True`.
        - Hexadecimal string if `as_hex=True`.
    """
    try:
        if not os.path.exists(path):
            raise SandyieException(f"BIN file not found: {path}")

        with open(path, "rb") as f:
            content = f.read()

        if as_base64:
            content = base64.b64encode(content).decode("utf-8")
        elif as_hex:
            content = content.hex()

        logger.info("[BinReader] Successfully read BIN file: {}".format(path))
        return content

    except Exception as e:
        raise SandyieException("Failed to read the .bin file", e)
