"""Tests for the main Cleaner class."""

import unittest

from tidyname import Cleaner, CleanerConfig, CleaningResult


class TestCleaner(unittest.TestCase):
    """Test cases for Cleaner class."""
    
    def setUp(self) -> None:
        """Set up test cleaner instance."""
        self.cleaner = Cleaner()
    
    def test_cleaner_initialization_default(self) -> None:
        """Test cleaner initializes with default config."""
        cleaner = Cleaner()
        self.assertIsInstance(cleaner.config, CleanerConfig)
        self.assertTrue(cleaner.config.remove_corporate_suffixes)
        self.assertTrue(cleaner.config.preserve_known_brands)
    
    def test_cleaner_initialization_custom_config(self) -> None:
        """Test cleaner initializes with custom config."""
        config = CleanerConfig(
            remove_corporate_suffixes=False,
            preserve_known_brands=False
        )
        cleaner = Cleaner(config=config)
        self.assertFalse(cleaner.config.remove_corporate_suffixes)
        self.assertFalse(cleaner.config.preserve_known_brands)
    
    def test_clean_empty_input(self) -> None:
        """Test cleaning empty input."""
        result = self.cleaner.clean("")
        self.assertEqual(result.original, "")
        self.assertEqual(result.cleaned, "")
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.confidence_level, "low")
        self.assertFalse(result.changes_made)
        self.assertEqual(result.reason, "Empty input provided")
        
        # Test whitespace-only input
        result = self.cleaner.clean("   ")
        self.assertEqual(result.cleaned, "")
        self.assertEqual(result.reason, "Empty input provided")
    
    def test_clean_basic_corporation(self) -> None:
        """Test cleaning basic corporation suffixes."""
        test_cases = [
            ("Apple Inc.", "Apple"),
            ("Microsoft Corporation", "Microsoft"),
            ("Google LLC", "Google"),
            ("Amazon.com, Inc.", "Amazon.com"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.cleaner.clean(original)
                self.assertEqual(result.original, original)
                self.assertEqual(result.cleaned, expected)
                self.assertTrue(result.changes_made)
                self.assertGreater(result.confidence, 0.8)
                self.assertEqual(result.confidence_level, "high")
    
    def test_clean_preserve_brands(self) -> None:
        """Test preservation of known brands."""
        result = self.cleaner.clean("The Limited")
        self.assertEqual(result.original, "The Limited")
        self.assertEqual(result.cleaned, "The Limited")
        self.assertFalse(result.changes_made)
        self.assertIn("brand", result.reason.lower())
    
    def test_clean_multiple_suffixes(self) -> None:
        """Test cleaning names with multiple suffixes."""
        result = self.cleaner.clean("Tech Solutions Inc. LLC")
        self.assertEqual(result.cleaned, "Tech Solutions")
        self.assertTrue(result.changes_made)
        self.assertGreater(result.confidence, 0.7)
    
    def test_clean_international_suffixes(self) -> None:
        """Test cleaning international suffixes."""
        test_cases = [
            ("Toyota Motor Co., Ltd.", "Toyota Motor"),
            ("Samsung Electronics GmbH", "Samsung Electronics"),
            ("Siemens AG", "Siemens"),
            ("L'Oréal S.A.", "L'Oréal"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.cleaner.clean(original)
                self.assertEqual(result.cleaned, expected)
                self.assertTrue(result.changes_made)
    
    def test_clean_case_variations(self) -> None:
        """Test cleaning handles case variations."""
        test_cases = [
            ("APPLE INC.", "APPLE"),
            ("microsoft corporation", "microsoft"),
            ("GoOgLe LlC", "GoOgLe"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.cleaner.clean(original)
                self.assertEqual(result.cleaned, expected)
                self.assertTrue(result.changes_made)
    
    def test_clean_no_suffix(self) -> None:
        """Test cleaning names without corporate suffixes."""
        test_cases = ["Apple", "Microsoft", "Google", "Amazon"]
        
        for name in test_cases:
            with self.subTest(name=name):
                result = self.cleaner.clean(name)
                self.assertEqual(result.cleaned, name)
                self.assertFalse(result.changes_made)
                self.assertIn("No corporate suffixes found", result.reason)
    
    def test_clean_batch(self) -> None:
        """Test batch cleaning functionality."""
        names = [
            "Apple Inc.",
            "Microsoft Corporation",
            "Google LLC",
            "Amazon",
            ""
        ]
        
        results = self.cleaner.clean_batch(names)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0].cleaned, "Apple")
        self.assertEqual(results[1].cleaned, "Microsoft")
        self.assertEqual(results[2].cleaned, "Google")
        self.assertEqual(results[3].cleaned, "Amazon")
        self.assertEqual(results[4].cleaned, "")
        
        # Verify each result is a CleaningResult
        for result in results:
            self.assertIsInstance(result, CleaningResult)
    
    def test_configure_valid_params(self) -> None:
        """Test updating configuration with valid parameters."""
        self.cleaner.configure(
            remove_corporate_suffixes=False,
            preserve_known_brands=False,
            min_confidence_threshold=0.9
        )
        
        self.assertFalse(self.cleaner.config.remove_corporate_suffixes)
        self.assertFalse(self.cleaner.config.preserve_known_brands)
        self.assertEqual(self.cleaner.config.min_confidence_threshold, 0.9)
    
    def test_configure_invalid_params(self) -> None:
        """Test updating configuration with invalid parameters."""
        with self.assertRaises(ValueError) as context:
            self.cleaner.configure(invalid_param=True)
        
        self.assertIn("Unknown configuration parameter: invalid_param", 
                     str(context.exception))
    
    def test_clean_with_disabled_removal(self) -> None:
        """Test cleaning with suffix removal disabled."""
        self.cleaner.configure(remove_corporate_suffixes=False)
        
        result = self.cleaner.clean("Apple Inc.")
        self.assertEqual(result.cleaned, "Apple Inc.")
        self.assertFalse(result.changes_made)
        self.assertIn("disabled", result.reason.lower())
    
    def test_clean_with_disabled_brand_preservation(self) -> None:
        """Test cleaning with brand preservation disabled."""
        self.cleaner.configure(preserve_known_brands=False)
        
        result = self.cleaner.clean("The Limited")
        self.assertEqual(result.cleaned, "The")
        self.assertTrue(result.changes_made)
        # Should not mention brand preservation in reason
        self.assertNotIn("brand", result.reason.lower())
    
    def test_confidence_levels(self) -> None:
        """Test different confidence levels are assigned correctly."""
        # High confidence - standard suffix
        result = self.cleaner.clean("Apple Inc.")
        self.assertEqual(result.confidence_level, "high")
        
        # Medium confidence - edge case or ambiguous
        result = self.cleaner.clean("Services LLC")
        self.assertIn(result.confidence_level, ["medium", "high"])
        
        # Low confidence - empty input
        result = self.cleaner.clean("")
        self.assertEqual(result.confidence_level, "low")


if __name__ == "__main__":
    unittest.main()