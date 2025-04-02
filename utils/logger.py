import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger():
    """
    Set up logging configuration with both console and file output.
    Logs will be saved in the logs directory with rotation.
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create a timestamp for the log file name
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            RotatingFileHandler(
                f'logs/transcriber_{timestamp}.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    
    return logger

# Create a default logger instance
logger = setup_logger() 