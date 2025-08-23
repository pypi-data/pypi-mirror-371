"""Tests for type definitions."""

import unittest
from tidyname.types import (
    CleaningResult,
    TermMatch,
    CleanerConfig,
    ConfidenceLevel
)


class TestTypes(unittest.TestCase):
    """Test type definitions."""

    def test_cleaning_result_instantiation(self):
        """Test that CleaningResult can be instantiated."""
        result = CleaningResult(
            original="Apple Inc.",
            cleaned="Apple",
            confidence=0.95,
            confidence_level="high",
            changes_made=True,
            reason="Removed: Inc."
        )
        
        self.assertEqual(result.original, "Apple Inc.")
        self.assertEqual(result.cleaned, "Apple")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.confidence_level, "high")
        self.assertTrue(result.changes_made)
        self.assertEqual(result.reason, "Removed: Inc.")

    def test_term_match_instantiation(self):
        """Test that TermMatch can be instantiated."""
        match = TermMatch(
            term="LLC",
            position=10,
            category="limited_liability",
            normalized_term="llc"
        )
        
        self.assertEqual(match.term, "LLC")
        self.assertEqual(match.position, 10)
        self.assertEqual(match.category, "limited_liability")
        self.assertEqual(match.normalized_term, "llc")

    def test_cleaner_config_defaults(self):
        """Test CleanerConfig default values."""
        config = CleanerConfig()
        
        self.assertEqual(config.min_name_length, 2)
        self.assertTrue(config.preserve_known_entities)

    def test_cleaner_config_custom_values(self):
        """Test CleanerConfig with custom values."""
        config = CleanerConfig(
            min_name_length=3,
            preserve_known_entities=False
        )
        
        self.assertEqual(config.min_name_length, 3)
        self.assertFalse(config.preserve_known_entities)

    def test_confidence_level_enum(self):
        """Test ConfidenceLevel enum values."""
        self.assertEqual(ConfidenceLevel.HIGH.value, "high")
        self.assertEqual(ConfidenceLevel.MEDIUM.value, "medium")
        self.assertEqual(ConfidenceLevel.LOW.value, "low")


if __name__ == "__main__":
    unittest.main()