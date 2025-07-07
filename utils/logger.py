import logging
import os
from logging.handlers import RotatingFileHandler

# Define base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "catalog_manager.log")

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create logger
logger = logging.getLogger("catalog_manager")
logger.setLevel(logging.DEBUG)  # Log everything

# Prevent adding duplicate handlers
if not logger.handlers:
    # Rotating File Handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

# Prevent duplicate logs with other loggers (like Flask's default)
logger.propagate = False
