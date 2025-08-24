"""Configuration for a single translation task."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TranslationConfig:
    """Configuration for a single translation task."""
    input_path: Path
    output_path: Path
    srt_file: str = ""
    target_language: str = "persian"
    prompt: str = ""
    batch_size: int = 300
    api_key: str = ""

    def __post_init__(self):
        if self.batch_size <= 0:
            raise ValueError("Batch size must be > 0")
        if not self.api_key.strip():
            raise ValueError("API key is required")
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input path not found: {self.input_path}")

    @property
    def input_file(self) -> Path:
        """Return the full path to the input file."""
        return self.input_path / self.srt_file

    @property
    def output_file(self) -> Path:
        """Return the full path to the output file."""
        return self.output_path / self.srt_file

    @property
    def short_prompt(self) -> str:
        """Return a shortened version of the prompt (max 150 characters)."""
        if not self.prompt:
            return ""
        return self.prompt[:150] + ("..." if len(self.prompt) > 150 else "")
