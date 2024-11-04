import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from rich.logging import RichHandler


def get_logger(
    name: str,
    log_filename: str = "logs/llm.log",
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)

        console_handler = RichHandler(level=level)

        log_path = Path(log_filename).parent
        _ = log_path.exists() or log_path.mkdir(exist_ok=True, parents=True)

        file_handler = RotatingFileHandler(
            filename=log_filename,
            mode="a",
            maxBytes=2 * 1024 * 1024,  # 2MB
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        logger.info(f"[{name}] Logging at {log_filename}...")

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
