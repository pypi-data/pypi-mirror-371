"""Core data types for configuration system."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..rules import Rule
from .models import ConfigFile


class SourceType(Enum):
    """Configuration source types."""

    DEFAULT = "default"
    USER = "user"
    SHARED = "shared"
    LOCAL = "local"


@dataclass
class ConfigurationSource:
    """Represents a configuration source (file location and metadata)."""

    source_type: SourceType
    path: Path
    exists: bool

    @property
    def display_name(self) -> str:
        """Human-friendly name for this source type."""
        return {
            SourceType.DEFAULT: "Default",
            SourceType.USER: "User",
            SourceType.SHARED: "Shared",
            SourceType.LOCAL: "Local",
        }[self.source_type]


@dataclass
class RawConfiguration:
    """Raw configuration data loaded from YAML before processing."""

    source: ConfigurationSource
    data: ConfigFile


@dataclass
class Configuration:
    """Final processed configuration with merged rules."""

    sources: list[ConfigurationSource] = field(default_factory=list)
    default_rules: bool | list[str] = True
    rules: list[Rule] = field(default_factory=list)

    @property
    def total_rules(self) -> int:
        """Total number of rules in configuration."""
        return len(self.rules)

    @property
    def active_rules(self) -> list[Rule]:
        """List of enabled rules."""
        return [rule for rule in self.rules if rule.enabled]

    @property
    def disabled_rules(self) -> list[Rule]:
        """List of disabled rules."""
        return [rule for rule in self.rules if not rule.enabled]
