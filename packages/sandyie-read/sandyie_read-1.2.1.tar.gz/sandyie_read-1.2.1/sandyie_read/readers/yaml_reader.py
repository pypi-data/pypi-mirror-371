import yaml
from sandyie_read.logging_config import logger
from sandyie_read.exceptions import SandyieException

def read_yaml(file_path, *args, **kwargs):
    """
    Reads data from a YAML file.
    Accepts additional parameters for open() and yaml.safe_load().
    """
    try:
        # Extract file-handling arguments
        encoding = kwargs.pop("encoding", "utf-8")
        errors = kwargs.pop("errors", "strict")

        with open(file_path, "r", encoding=encoding, errors=errors) as file:
            data = yaml.safe_load(file, *args, **kwargs)
            logger.info(f"[YAMLReader] Successfully read YAML file: {file_path}")
            return data
    except FileNotFoundError:
        logger.error(f"YAML file not found: {file_path}")
        raise SandyieException(f"YAML file not found: {file_path}")
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        raise SandyieException(f"YAML parsing error: {e}")
    except Exception as e:
        logger.error(f"Failed to read YAML file: {e}")
        raise SandyieException(f"Failed to read YAML file: {file_path}. Error: {str(e)}")
