# markdown_reader.py

import os
import io
import logging
from sandyie_read.exceptions import SandyieException

logger = logging.getLogger(__name__)

def read_md(path, *args, **kwargs):
    """
    Reads a Markdown file (.md or .markdown) and returns its content as a string.

    :param path: Path to the markdown file
    :return: str – the raw Markdown text
    """
    try:
        if not os.path.exists(path):
            raise SandyieException(f"Markdown file not found: {path}")

        with io.open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        logger.info(f"[MarkdownReader] Successfully read Markdown file: {path}")
        return text

    except SandyieException:
        raise  # already handled

    except Exception as e:
        logger.error(f"[MarkdownReader] Failed to read Markdown file: {path} | Error: {e}")
        raise SandyieException("Failed to read the Markdown file", e)
