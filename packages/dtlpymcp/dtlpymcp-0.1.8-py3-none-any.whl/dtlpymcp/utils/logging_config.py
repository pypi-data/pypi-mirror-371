"""
Centralized logging configuration for dtlpymcp.
Handles file and console logging with configurable verbosity levels.
"""

import logging
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "DEBUG") -> None:
    """
    Set up logging configuration for the entire dtlpymcp application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.DEBUG)
    
    # Setup logging directory and file
    log_dir = Path.home() / ".dataloop" / "mcplogs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    
    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # File handler with timestamp
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    
    # Console handler (default format)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(fmt="[%(levelname)s] %(name)s: %(message)s"))
    
    # Configure root logger
    logging.basicConfig(level=level, handlers=[file_handler, console_handler])
    
    # Get the main logger
    logger = logging.getLogger("dtlpymcp")
    logger.info(f"Logging configured with level: {log_level.upper()}")
    logger.info(f"Log file: {log_file}")


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (optional, defaults to "dtlpymcp")
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if name is None:
        return logging.getLogger("dtlpymcp")
    return logging.getLogger(f"dtlpymcp.{name}")
