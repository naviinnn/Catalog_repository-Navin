import logging
import os

# Create logs folder if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Create logger
logger = logging.getLogger("catalog_manager")
logger.setLevel(logging.DEBUG)  # Log everything

# Prevent adding duplicate handlers
if not logger.handlers:
    # File handler only (no console)
    file_handler = logging.FileHandler("logs/catalog_manager.log")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
