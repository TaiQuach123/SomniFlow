import os
import json
import logging
import logging.config
from pathlib import Path


def setup_logging(config_path: str | Path = "./config/logging_dict_config.json"):
    """Setup logging configuration

    Args:
        config_path: Path to the logging config JSON file
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Logging config file not found at {config_path}")

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    with open(config_path) as f:
        config = json.load(f)

    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
