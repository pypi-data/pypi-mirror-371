import cv2
from sandyie_read.exceptions import SandyieException
from sandyie_read.logging_config import logger


def read_image(file_path, *args, **kwargs):
    try:
        image = cv2.imread(file_path, *args, **kwargs)
        if image is None:
            raise SandyieException("Image file could not be read or is invalid.")
        logger.info(f"Successfully read image: {file_path}")
        return image
    except SandyieException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while reading image: {e}")
        raise SandyieException(f"An unexpected error occurred while reading the image: {e}")
