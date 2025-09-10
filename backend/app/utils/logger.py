import logging
from app.core.config import settings

# Configure logging
logger = logging.getLogger("finance_tracker")
logger.setLevel(settings.LOG_LEVEL)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(settings.LOG_LEVEL)

# Formatter
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
ch.setFormatter(formatter)

# Avoid duplicate handlers
if not logger.handlers:
    logger.addHandler(ch)
