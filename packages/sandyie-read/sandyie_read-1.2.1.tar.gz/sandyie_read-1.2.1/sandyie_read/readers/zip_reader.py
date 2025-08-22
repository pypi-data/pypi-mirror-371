import zipfile
import pandas as pd
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_zip(path, file_name=None, *args, **kwargs):
    """
    Reads a .zip file containing one or more supported files 
    (.csv, .tsv, .xls, .xlsx) and returns its content as a pandas DataFrame.

    Parameters
    ----------
    path : str
        Path to the ZIP archive.
    file_name : str, optional
        Specific file inside the archive to read. If None, the first supported file is used.
    *args, **kwargs :
        Additional arguments passed to pandas.read_csv or pandas.read_excel.
    """
    try:
        with zipfile.ZipFile(path, 'r') as z:
            supported_exts = ('.csv', '.tsv', '.xls', '.xlsx')
            supported_files = [f for f in z.namelist() if f.lower().endswith(supported_exts)]

            if not supported_files:
                raise SandyieException(
                    "No supported files (.csv, .tsv, .xls, .xlsx) found in the ZIP archive.", None
                )

            # Pick file
            if file_name:
                if file_name not in supported_files:
                    raise SandyieException(
                        f"Specified file '{file_name}' not found in ZIP or not supported.\n"
                        f"Available files: {supported_files}", None
                    )
                target_file = file_name
            else:
                target_file = supported_files[0]  # Default: first file

            # Read file
            with z.open(target_file) as f:
                if target_file.endswith('.csv'):
                    df = pd.read_csv(f, *args, **kwargs)
                elif target_file.endswith('.tsv'):
                    df = pd.read_csv(f, sep='\t', *args, **kwargs)
                else:  # Excel formats
                    df = pd.read_excel(f, *args, **kwargs)

            logger.info(f"[ZipReader] Successfully read '{target_file}' from ZIP: {path}")
            return df

    except SandyieException:
        raise
    except Exception as e:
        logger.error(f"[ZipReader] Failed to read ZIP file {path}: {e}")
        raise SandyieException("Failed to read the .zip file", e)
