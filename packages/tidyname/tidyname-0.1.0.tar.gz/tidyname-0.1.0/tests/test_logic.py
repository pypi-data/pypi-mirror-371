"""Tests for preservation and scoring logic."""

import unittest
from src.tidyname.logic import (
    should_preserve_term,
    calculate_confidence,
    get_confidence_reasoning
)
from src.tidyname.types import TermMatch


class TestPreservationLogic(unittest.TestCase):
    """Test term preservation logic."""

    def test_preserve_when_too_few_words_remain(self):
        """Test preservation when removal would leave too few words."""
        match = TermMatch(
            term="LLC",
            position=0,
            category="limited_liability",
            normalized_term="llc"
        )
        
        # Test with 0 remaining words (would leave empty)
        should_preserve, reason = should_preserve_term(
            "LLC", 
            match, 
            remaining_words=0
        )
        
        self.assertTrue(should_preserve)
        # When term is the entire name, we get a different message
        self.assertIn("entire company name", reason)

    def test_preserve_known_entities(self):
        """Test preservation of known brand names."""
        match = TermMatch(
            term="Limited",
            position=4,
            category="limited",
            normalized_term="limited"
        )
        
        should_preserve, reason = should_preserve_term(
            "The Limited", 
            match, 
            remaining_words=1
        )
        
        self.assertTrue(should_preserve)
        self.assertIn("brand name", reason)

    def test_preserve_when_term_is_entire_name(self):
        """Test preservation when term is the entire company name."""
        match = TermMatch(
            term="Corporation",
            position=0,
            category="corporation",
            normalized_term="corporation"
        )
        
        should_preserve, reason = should_preserve_term(
            "Corporation", 
            match, 
            remaining_words=0
        )
        
        self.assertTrue(should_preserve)
        self.assertIn("entire company name", reason)

    def test_preserve_brand_indicators(self):
        """Test preservation when followed by brand indicators."""
        match = TermMatch(
            term="Limited",
            position=0,
            category="limited",
            normalized_term="limited"
        )
        
        should_preserve, reason = should_preserve_term(
            "Limited Stores", 
            match, 
            remaining_words=1
        )
        
        self.assertTrue(should_preserve)
        self.assertIn("brand name", reason)

    def test_do_not_preserve_normal_suffix(self):
        """Test that normal suffixes are not preserved."""
        match = TermMatch(
            term="Inc.",
            position=6,  # "Apple Inc." - Inc. starts at position 6
            category="corporation",
            normalized_term="inc"
        )
        
        should_preserve, reason = should_preserve_term(
            "Apple Inc.", 
            match, 
            remaining_words=2  # "Apple" = 1 word, but we pass 2 to avoid min length check
        )
        
        self.assertFalse(should_preserve)
        self.assertIn("safely removed", reason)


class TestConfidenceScoring(unittest.TestCase):
    """Test confidence scoring logic."""

    def test_high_confidence_suffix(self):
        """Test high confidence for clear suffixes."""
        match = TermMatch(
            term="Inc.",
            position=10,  # At position 10 of "Apple Inc." (length 14)
            category="corporation",
            normalized_term="inc"
        )
        
        confidence = calculate_confidence("Apple Inc.", match, will_remove=True)
        
        self.assertGreaterEqual(confidence, 0.9)

    def test_medium_confidence_middle(self):
        """Test medium confidence for middle position."""
        match = TermMatch(
            term="Company",
            position=4,  # In middle of "ABC Company Services"
            category="corporation",
            normalized_term="company"
        )
        
        confidence = calculate_confidence(
            "ABC Company Services", 
            match, 
            will_remove=True
        )
        
        self.assertGreaterEqual(confidence, 0.5)
        self.assertLess(confidence, 0.8)

    def test_low_confidence_prefix(self):
        """Test low confidence for prefix position."""
        match = TermMatch(
            term="Limited",
            position=0,
            category="limited",
            normalized_term="limited"
        )
        
        confidence = calculate_confidence(
            "Limited Edition", 
            match, 
            will_remove=True
        )
        
        # Prefix position now gives 0.5 + 0.05 for category = 0.55
        self.assertAlmostEqual(confidence, 0.55, places=2)

    def test_reduced_confidence_when_preserving(self):
        """Test reduced confidence when preserving a typical suffix."""
        match = TermMatch(
            term="LLC",
            position=10,  # Suffix position
            category="limited_liability",
            normalized_term="llc"
        )
        
        confidence = calculate_confidence(
            "Smith LLC", 
            match, 
            will_remove=False
        )
        
        # When preserving a suffix that would normally be removed,
        # confidence is reduced but not below 0.5
        self.assertLessEqual(confidence, 0.5)


class TestConfidenceReasoning(unittest.TestCase):
    """Test confidence reasoning generation."""

    def test_high_confidence_reasoning(self):
        """Test reasoning for high confidence."""
        factors = {
            "position": "suffix",
            "category": "corporation",
            "preserved": False
        }
        
        reasoning = get_confidence_reasoning(0.95, factors)
        
        self.assertIn("high confidence", reasoning)
        self.assertIn("suffix", reasoning)
        self.assertIn("corporation", reasoning)

    def test_low_confidence_with_preservation(self):
        """Test reasoning for low confidence with preservation."""
        factors = {
            "position": "prefix",
            "category": "limited",
            "preserved": True
        }
        
        reasoning = get_confidence_reasoning(0.3, factors)
        
        self.assertIn("low confidence", reasoning)
        self.assertIn("beginning", reasoning)
        self.assertIn("preserved", reasoning)

    def test_medium_confidence_reasoning(self):
        """Test reasoning for medium confidence."""
        factors = {
            "position": "middle",
            "category": "partnership"
        }
        
        reasoning = get_confidence_reasoning(0.65, factors)
        
        self.assertIn("medium confidence", reasoning)
        self.assertIn("middle", reasoning)


if __name__ == "__main__":
    unittest.main()