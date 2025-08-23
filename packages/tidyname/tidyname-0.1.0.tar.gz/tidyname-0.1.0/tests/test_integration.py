"""Integration tests for TidyName package."""

import unittest
from typing import List

from tidyname import Cleaner, CleanerConfig, CleaningResult


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cleaner = Cleaner()
    
    def test_end_to_end_workflow(self) -> None:
        """Test complete workflow from input to output."""
        # Real-world company names
        companies = [
            "Apple Inc.",
            "Microsoft Corporation",
            "Alphabet Inc.",
            "Amazon.com, Inc.",
            "Meta Platforms, Inc.",
            "Tesla, Inc.",
            "Netflix, Inc.",
            "The Walt Disney Company",
            "Berkshire Hathaway Inc.",
            "Johnson & Johnson"
        ]
        
        results = self.cleaner.clean_batch(companies)
        
        # Verify all results
        self.assertEqual(len(results), len(companies))
        
        expected_cleaned = [
            "Apple",
            "Microsoft", 
            "Alphabet",
            "Amazon.com",
            "Meta Platforms",
            "Tesla",
            "Netflix",
            "The Walt Disney",  # "Company" removed
            "Berkshire Hathaway",
            "Johnson & Johnson"  # No changes
        ]
        
        for i, (result, expected) in enumerate(zip(results, expected_cleaned)):
            with self.subTest(company=companies[i]):
                self.assertEqual(result.cleaned, expected)
                self.assertIsInstance(result.confidence, float)
                self.assertIn(result.confidence_level, ["low", "medium", "high"])
                self.assertIsInstance(result.changes_made, bool)
                self.assertIsInstance(result.reason, str)
    
    def test_international_companies(self) -> None:
        """Test international company names."""
        international_companies = [
            ("Toyota Motor Corporation", "Toyota Motor"),
            ("Samsung Electronics Co., Ltd.", "Samsung Electronics"),
            ("Siemens AG", "Siemens"),
            ("Nestlé S.A.", "Nestlé"),
            ("ASML Holding N.V.", "ASML Holding"),
            ("Volkswagen AG", "Volkswagen"),
            ("TSMC Ltd.", "TSMC"),
            ("Unilever N.V.", "Unilever"),
            ("L'Oréal S.A.", "L'Oréal")
        ]
        
        for original, expected in international_companies:
            with self.subTest(company=original):
                result = self.cleaner.clean(original)
                self.assertEqual(result.cleaned, expected)
                if result.changes_made:
                    self.assertGreater(result.confidence, 0.5)
    
    def test_brand_preservation_integration(self) -> None:
        """Test brand preservation in real scenarios."""
        brand_cases = [
            ("The Limited", "The Limited", False),  # Preserve retail brand
            ("Limited Brands", "Limited Brands", False),  # Preserve parent company
            ("Apple Inc.", "Apple", True),  # Clear suffix
        ]
        
        for original, expected_cleaned, should_change in brand_cases:
            with self.subTest(company=original):
                result = self.cleaner.clean(original)
                self.assertEqual(result.cleaned, expected_cleaned)
                self.assertEqual(result.changes_made, should_change)
                
                if not should_change:
                    # Should have preservation reasoning
                    self.assertIn("Preserved", result.reason)


if __name__ == "__main__":
    unittest.main()