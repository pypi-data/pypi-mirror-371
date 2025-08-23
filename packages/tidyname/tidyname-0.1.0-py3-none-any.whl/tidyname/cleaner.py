"""Main cleaner implementation for TidyName."""

from typing import Any

from .logic import apply_cleaning_logic
from .terms import find_terms_in_name, normalize_term
from .types import CleanerConfig, CleaningResult


class Cleaner:
    """Main cleaner class for company name processing."""
    
    def __init__(self, config: CleanerConfig | None = None) -> None:
        """Initialize cleaner with optional configuration.
        
        Args:
            config: Optional configuration settings
        """
        self.config = config or CleanerConfig()
    
    def clean(self, company_name: str) -> CleaningResult:
        """Clean a single company name.
        
        Args:
            company_name: Company name to clean
            
        Returns:
            CleaningResult with cleaned name and metadata
        """
        # Handle empty input
        if not company_name or not company_name.strip():
            return CleaningResult(
                original=company_name,
                cleaned="",
                confidence=0.0,
                confidence_level="low",
                changes_made=False,
                reason="Empty input provided"
            )
        
        # Find all term matches
        matches = find_terms_in_name(company_name)
        
        # Apply cleaning logic
        result = apply_cleaning_logic(
            original=company_name,
            normalized=company_name.strip(),
            matches=matches,
            config=self.config
        )
        
        return result
    
    def clean_batch(self, company_names: list[str]) -> list[CleaningResult]:
        """Clean multiple company names.
        
        Args:
            company_names: List of company names to clean
            
        Returns:
            List of CleaningResult objects
        """
        return [self.clean(name) for name in company_names]
    
    def configure(self, **kwargs: Any) -> None:
        """Update configuration settings.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")