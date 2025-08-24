"""Prompt Library for managing prompts."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class Prompt:
    """Individual prompt item."""
    name: str
    description: str
    created_at: Optional[str] = None
    last_used: Optional[str] = None

    def __post_init__(self):
        """Set creation item if not provided."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class PromptLibrary:
    """Collection of prompts with metadata."""
    prompts: Dict[str, Prompt] = field(default_factory=dict)
    version: str = "1.0"

    def add_prompt(self, name: str, description: str) -> bool:
        """Add a new prompt."""
        if name in self.prompts:
            return False

        self.prompts[name] = Prompt(name=name, description=description)
        return True

    def update_prompt(self, name: str, description: str) -> bool:
        """Update an existing prompt."""
        if name not in self.prompts:
            return False

        self.prompts[name].description = description
        return True

    def delete_prompt(self, name: str) -> bool:
        """Delete a prompt."""
        if name not in self.prompts:
            return False

        del self.prompts[name]
        return True

    def get_prompt_names(self) -> list[str]:
        """Get a list of prompt names."""
        return list(self.prompts.keys())

    def get_prompt_descriptions(self) -> Dict[str, str]:
        """Get dictionary of name -> description mapping."""
        return {name: prompt.description for name, prompt in self.prompts.items()}

    def mark_used(self, name: str):
        """Mark prompt as recently used."""
        if name in self.prompts:
            self.prompts[name].last_used = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert dictionary from JSON serialization."""
        return {
            'prompts': {name: asdict(prompt) for name, prompt in self.prompts.items()},
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptLibrary':
        """Create instance from dictionary."""
        prompts_data = data.get('prompts', {})
        prompts = {}

        for name, prompt_data in prompts_data.items():
            prompts[name] = Prompt(**prompt_data)

        return cls(
            prompts=prompts,
            version=data.get('version', '1.0')
        )

    @classmethod
    def from_legacy_dict(cls, data: Dict[str, str]) -> 'PromptLibrary':
        """Create instance from legacy dictionary."""
        collection = cls()
        for name, description in data.items():
            collection.add_prompt(name, description)
        return collection
