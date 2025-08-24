"""Log setup module"""

import sys
import logging
import platformdirs
import colorlog


def setup_logging(debug: bool) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO

    log_dir = platformdirs.user_data_path() / "srtify" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(color_formatter)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_dir / "srtify.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    srtify = logging.getLogger("srtify")
    srtify.setLevel(level)
    srtify.addHandler(console_handler)
    srtify.addHandler(file_handler)

    # srtify.propagate = False
