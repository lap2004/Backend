from loguru import logger
import sys
import os

from app.config import settings

def setup_logger():
    log_path = settings.LOG_PATH or "logs/app.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger.remove() 
    logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
    logger.add(log_path, rotation="1 MB", retention="7 days", enqueue=True, level="INFO")
