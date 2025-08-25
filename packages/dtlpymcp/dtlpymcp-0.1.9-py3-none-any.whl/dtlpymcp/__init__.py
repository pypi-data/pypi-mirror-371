from .utils.dtlpy_context import DataloopContext, MCPSource
import logging
from datetime import datetime
from pathlib import Path

__version__ = "0.1.9"


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
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

# Get the main logger
logger = logging.getLogger("dtlpymcp")
logger.info(f"Logging configured with level: DEBUG")
logger.info(f"Log file: {log_file}")
