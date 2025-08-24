"""Configuration settings."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ApiConfig:
    """API Configuration settings."""
    gemini_key: str = ""

    def is_valid(self) -> bool:
        """Check if the api key is valid"""
        return bool(self.gemini_key.strip())


@dataclass
class PathConfig:
    """Directory configuration settings."""
    input_dir: str = ""
    output_dir: str = ""

    def __post_init__(self):
        """Expand user paths after initialization."""
        if self.input_dir:
            self.input_dir = os.path.expanduser(self.input_dir)
        if self.output_dir:
            self.output_dir = os.path.expanduser(self.output_dir)

    def validate(self) -> bool:
        """Validate directory paths."""
        if not self.input_dir or not self.output_dir:
            return False

        try:
            Path(self.input_dir).mkdir(parents=True, exist_ok=True)
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False


@dataclass
class TranslatorConfig:
    """Translation configuration settings."""
    default_language: str = "Persian"
    batch_size: int = 300

    def __post_init__(self):
        if self.batch_size <= 0:
            self.batch_size = 300
