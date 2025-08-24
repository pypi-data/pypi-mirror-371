"""Settings for the application."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any

from srtify.models.config import ApiConfig, PathConfig, TranslatorConfig


@dataclass
class AppSettings:
    """Application settings."""
    api: ApiConfig = field(default_factory=ApiConfig)
    directories: PathConfig = field(default_factory=PathConfig)
    translation: TranslatorConfig = field(default_factory=TranslatorConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Create instance from dictionary."""
        api_data = data.get('api', {})
        dir_data = data.get('directories', {})
        trans_data = data.get('translation', {})

        return cls(
            api=ApiConfig(**api_data),
            directories=PathConfig(**dir_data),
            translation=TranslatorConfig(**trans_data)
        )

    def validate(self) -> bool:
        """Validate settings."""
        return (self.api.is_valid() and
                self.directories.validate() and
                self.translation.batch_size > 0)
