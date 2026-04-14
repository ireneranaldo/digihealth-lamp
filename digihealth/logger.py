import logging
import os
from .config import config

def setup_logging():
    """Setup structured logging."""
    # Expand user path (~) if present
    log_file = config.logging.file
    if log_file and log_file.startswith('~'):
        log_file = os.path.expanduser(log_file)

    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

logger = logging.getLogger(__name__)