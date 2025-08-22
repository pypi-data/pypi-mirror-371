import pandas as pd
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_tsv(path, *args, **kwargs):
    """
    Reads a TSV (.tsv) file and returns a pandas DataFrame.
    Accepts all parameters supported by pandas.read_csv.
    """
    try:
        df = pd.read_csv(path, sep="\t", *args, **kwargs)
        logger.info(f"[TSVReader] Successfully read TSV file: {path}")
        return df
    except FileNotFoundError:
        logger.error(f"TSV file not found: {path}")
        raise SandyieException(f"TSV file not found: {path}")
    except Exception as e:
        logger.exception("Failed to read TSV file.")
        raise SandyieException(f"Failed to read the TSV file: {str(e)}")
