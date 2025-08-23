"""Type definitions for the tidyname package."""

from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level categories for cleaning operations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CleaningResult:
    """Result of a company name cleaning operation."""
    original: str
    cleaned: str
    confidence: float
    confidence_level: str
    changes_made: bool
    reason: str


@dataclass
class TermMatch:
    """Internal representation of a matched term in a company name."""
    term: str
    position: int
    category: str
    normalized_term: str


@dataclass
class CleanerConfig:
    """Configuration options for the Cleaner."""
    min_name_length: int = 2
    preserve_known_entities: bool = True
    remove_corporate_suffixes: bool = True
    preserve_known_brands: bool = True
    min_confidence_threshold: float = 0.5