import logging
import os

# Determine the absolute path to the project root directory.
# __file__ is the path to the current script (logger.py).
# os.path.abspath(__file__) gives the absolute path to logger.py.
# os.path.dirname() gets the directory of logger.py (Job Search/src/).
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of SRC_DIR (Job Search/). This is the project root.
PROJECT_ROOT = os.path.dirname(SRC_DIR)
# Define the logs directory path relative to the project root.
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

def setup_logger():
    """
    Set up logging configuration with both file and console handlers.
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create the logs directory if it doesn't already exist.
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the base logger level to DEBUG

    # Create a file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)  # Log everything to the file

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Log only INFO and above to the console

    # Define a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
