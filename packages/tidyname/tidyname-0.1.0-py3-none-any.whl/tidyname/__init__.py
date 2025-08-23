"""TidyName - Intelligent company name cleaning for Python."""

from .cleaner import Cleaner
from .types import CleanerConfig, CleaningResult

__version__ = "0.1.0"
__all__ = ["Cleaner", "CleanerConfig", "CleaningResult"]