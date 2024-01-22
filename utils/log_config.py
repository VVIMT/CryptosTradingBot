import logging
import os
import datetime
from logging.handlers import RotatingFileHandler

# Define a custom log level for resource consumption
RESOURCE_CONSUMPTION_LEVEL = 60
logging.addLevelName(RESOURCE_CONSUMPTION_LEVEL, "RESOURCE_CONSUMPTION")

class ErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR

def setup_logging(debug_mode=False):
    log_dir = os.path.join(os.path.dirname(__file__), '../Logs')
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    # Debug log handler (logs everything up to DEBUG level)
    debug_handler = create_rotating_file_handler(log_dir, 'debug.log', logging.DEBUG, formatter)
    debug_handler.addFilter(LevelFilter(logging.DEBUG))
    logger.addHandler(debug_handler)

    # Error log handler (logs only ERROR and CRITICAL)
    error_handler = create_rotating_file_handler(log_dir, 'error.log', logging.ERROR, formatter)
    error_handler.addFilter(ErrorFilter())
    logger.addHandler(error_handler)

    # Info log handler (logs INFO and WARNING, excludes RESOURCE_CONSUMPTION)
    info_handler = create_rotating_file_handler(log_dir, 'info.log', logging.INFO, formatter)
    info_handler.addFilter(LevelFilter(logging.INFO))
    logger.addHandler(info_handler)

    # Custom handler for resource consumption
    setup_resource_consumption_logger(log_dir, formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def create_rotating_file_handler(log_dir, file_name, level, formatter):
    log_file = os.path.join(log_dir, file_name)
    handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

def setup_resource_consumption_logger(log_dir, formatter):
    resource_logger = logging.getLogger('resource_consumption')
    resource_logger.setLevel(RESOURCE_CONSUMPTION_LEVEL)
    resource_logger.propagate = False  # Prevents passing logs up to the root logger

    # Generating a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    resource_file_handler = create_rotating_file_handler(log_dir, f"{timestamp}_resource_consumption.log", RESOURCE_CONSUMPTION_LEVEL, formatter)
    resource_logger.addHandler(resource_file_handler)

class LevelFilter(logging.Filter):
    """
    Filter that only allows log records of a specific level.
    """
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno <= self.level
