from pathlib import Path

from promptboot.config import config
from promptboot.logs.log_manager import LogManager

LOG_DIR = Path(config["logging"]["dir"])
LOG_DIR.mkdir(exist_ok=True)
log_manager = LogManager(LOG_DIR, use_full_logging=True)

# 获取logger实例
# logger = log_manager.get_logger()
