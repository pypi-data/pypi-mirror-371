"""Tests for term definitions and matching."""

import unittest
from src.tidyname.terms import (
    CORPORATION_TERMS,
    LIMITED_TERMS,
    LLC_TERMS,
    PARTNERSHIP_TERMS,
    PROFESSIONAL_TERMS,
    INTERNATIONAL_TERMS,
    get_all_terms,
    normalize_term,
    get_term_variations,
    find_terms_in_name
)


class TestTermDefinitions(unittest.TestCase):
    """Test term category definitions."""

    def test_corporation_terms_exist(self):
        """Test that corporation terms are defined."""
        self.assertIn("company", CORPORATION_TERMS)
        self.assertIn("incorporated", CORPORATION_TERMS)
        self.assertIn("corporation", CORPORATION_TERMS)
        self.assertIn("inc.", CORPORATION_TERMS)
        self.assertIn("corp.", CORPORATION_TERMS)

    def test_limited_terms_exist(self):
        """Test that limited terms are defined."""
        self.assertIn("limited", LIMITED_TERMS)
        self.assertIn("ltd.", LIMITED_TERMS)
        self.assertIn("unlimited", LIMITED_TERMS)

    def test_llc_terms_exist(self):
        """Test that LLC terms are defined."""
        self.assertIn("llc", LLC_TERMS)
        self.assertIn("l.l.c.", LLC_TERMS)
        self.assertIn("plc", LLC_TERMS)

    def test_get_all_terms(self):
        """Test that get_all_terms returns all terms."""
        all_terms = get_all_terms()
        
        # Check that terms from each category are included
        self.assertIn("company", all_terms)
        self.assertIn("limited", all_terms)
        self.assertIn("llc", all_terms)
        self.assertIn("partnership", all_terms)
        self.assertIn("p.c.", all_terms)
        self.assertIn("gmbh", all_terms)


class TestTermNormalization(unittest.TestCase):
    """Test term normalization functionality."""

    def test_normalize_lowercase(self):
        """Test normalization converts to lowercase."""
        self.assertEqual(normalize_term("LLC"), "llc")
        self.assertEqual(normalize_term("Inc."), "inc")

    def test_normalize_removes_punctuation(self):
        """Test normalization removes punctuation."""
        self.assertEqual(normalize_term("L.L.C."), "llc")
        self.assertEqual(normalize_term("Inc."), "inc")
        self.assertEqual(normalize_term("Corp."), "corp")

    def test_normalize_removes_spaces(self):
        """Test normalization removes spaces."""
        self.assertEqual(normalize_term("L L C"), "llc")
        self.assertEqual(
            normalize_term("professional corporation"), 
            "professionalcorporation"
        )

    def test_normalize_preserves_ampersand(self):
        """Test normalization preserves & character."""
        self.assertEqual(normalize_term("& Co."), "&co")
        self.assertEqual(normalize_term("& co"), "&co")


class TestTermVariations(unittest.TestCase):
    """Test term variation generation."""

    def test_basic_variations(self):
        """Test basic case variations."""
        variations = get_term_variations("llc")
        self.assertIn("llc", variations)
        self.assertIn("LLC", variations)

    def test_dot_variations(self):
        """Test variations with and without dots."""
        variations = get_term_variations("L.L.C.")
        self.assertIn("L.L.C.", variations)
        self.assertIn("LLC", variations)
        self.assertIn("llc", variations)

    def test_space_variations(self):
        """Test variations with and without spaces."""
        variations = get_term_variations("& co")
        self.assertIn("& co", variations)
        self.assertIn("&co", variations)
        self.assertIn("&CO", variations)

    def test_no_duplicates(self):
        """Test that variations don't contain duplicates."""
        variations = get_term_variations("LLC")
        self.assertEqual(len(variations), len(set(variations)))


class TestTermMatching(unittest.TestCase):
    """Test term matching in company names."""

    def test_find_simple_suffix(self):
        """Test finding simple suffix terms."""
        matches = find_terms_in_name("Apple Inc.")
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].term, "Inc.")
        self.assertEqual(matches[0].position, 6)
        self.assertEqual(matches[0].category, "corporation")

    def test_find_multiple_terms(self):
        """Test finding multiple terms."""
        matches = find_terms_in_name("ABC Company LLC")
        
        self.assertEqual(len(matches), 2)
        terms = [m.term for m in matches]
        self.assertIn("Company", terms)
        self.assertIn("LLC", terms)

    def test_case_insensitive_matching(self):
        """Test case-insensitive matching."""
        matches1 = find_terms_in_name("Apple INC.")
        matches2 = find_terms_in_name("Apple inc.")
        matches3 = find_terms_in_name("Apple Inc.")
        
        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 1)
        self.assertEqual(len(matches3), 1)

    def test_word_boundary_matching(self):
        """Test that partial matches are not found."""
        matches = find_terms_in_name("Marketplace Solutions")
        
        # Should not match "plc" in "Marketplace"
        plc_matches = [m for m in matches if m.normalized_term == "plc"]
        self.assertEqual(len(plc_matches), 0)

    def test_punctuation_variations(self):
        """Test matching with punctuation variations."""
        matches1 = find_terms_in_name("Apple L.L.C.")
        matches2 = find_terms_in_name("Apple LLC")
        
        self.assertEqual(len(matches1), 1)
        self.assertEqual(len(matches2), 1)
        self.assertEqual(matches1[0].normalized_term, "llc")
        self.assertEqual(matches2[0].normalized_term, "llc")

    def test_position_tracking(self):
        """Test that positions are tracked correctly."""
        matches = find_terms_in_name("Limited Company Limited")
        
        self.assertEqual(len(matches), 3)
        # Check positions
        self.assertEqual(matches[0].position, 0)
        self.assertEqual(matches[1].position, 8)
        self.assertEqual(matches[2].position, 16)

    def test_ampersand_matching(self):
        """Test matching terms with ampersands."""
        matches = find_terms_in_name("Smith & Co.")
        
        # Should find both "& Co." and "Co."
        self.assertEqual(len(matches), 2)
        terms = [m.term for m in matches]
        self.assertIn("& Co.", terms)
        self.assertIn("Co.", terms)

    def test_international_terms(self):
        """Test matching international terms."""
        matches = find_terms_in_name("Siemens AG")
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].term, "AG")
        self.assertEqual(matches[0].category, "international")


if __name__ == "__main__":
    unittest.main()