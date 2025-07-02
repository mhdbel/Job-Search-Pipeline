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
    # Create the logs directory if it doesn't already exist.
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger()
