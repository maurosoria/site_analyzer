import logging
import sys
from typing import Optional

def init_logging(debug: bool = False, log_file: Optional[str] = None):
    """Initialize logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger()
    logger.setLevel(level)
    
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def highlight(message: str, level: str = "INFO"):
    """Highlight message with formatting"""
    if level == "FINAL":
        print(f"\n{'='*50}")
        print(f"  {message}")
        print(f"{'='*50}\n")
    elif level == "ERROR":
        print(f"\n[ERROR] {message}\n")
    elif level == "WARNING":
        print(f"\n[WARNING] {message}\n")
    else:
        print(f"\n[INFO] {message}\n")
