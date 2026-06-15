import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Sets up structured JSON logging for production."""
    logger = logging.getLogger("bitrix_gcp")
    logger.setLevel(level.upper())

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s %(lineno)d",
            datefmt="%Y-%m-%dT%H:%M:%SZ"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = setup_logging()
