"""Preservation and scoring logic for company name cleaning."""

from typing import Any

from .types import CleanerConfig, CleaningResult, TermMatch


def should_preserve_term(
    name: str, 
    term_match: TermMatch, 
    remaining_words: int
) -> tuple[bool, str]:
    """Determine if a term should be preserved in the company name.
    
    Args:
        name: The full company name.
        term_match: The matched term to evaluate.
        remaining_words: Number of words that would remain after removal.
        
    Returns:
        Tuple of (should_preserve, reason).
    """
    # Check if the entire name is just the term
    if name.strip().lower() == term_match.term.lower():
        return (
            True,
            f"Preserving '{term_match.term}' - it is the entire company name"
        )
    
    # Check for known entities that should be preserved
    name_lower = name.lower()
    
    # Known retail brands where "limited" is part of the name
    known_entities = [
        "the limited",
        "limited brands",
        "limited too",
    ]
    
    for entity in known_entities:
        if entity in name_lower:
            return (
                True, 
                f"Preserving '{term_match.term}' - appears to be part of brand name"
            )
    
    # Check if term is at the beginning and might be part of the name
    if term_match.position == 0:
        # Check if it's followed by a noun that suggests it's a brand
        words_after = name[term_match.position + len(term_match.term):].strip().split()
        if words_after:
            first_word_after = words_after[0].lower()
            # Common retail/brand indicators
            brand_indicators = [
                "store", "stores", "shop", "shops", "brands", 
                "edition", "collection", "express", "too"
            ]
            if first_word_after in brand_indicators:
                return (
                    True,
                    f"Preserving '{term_match.term}' - likely part of brand name"
                )
    
    # Check minimum name length AFTER other checks
    # Allow single-word company names (like "Apple" from "Apple Inc.")
    if remaining_words < 1:
        return (
            True, 
            f"Preserving '{term_match.term}' - removal would leave empty name"
        )
    
    # Default: don't preserve
    return (False, f"Term '{term_match.term}' can be safely removed")


def calculate_confidence(
    name: str, 
    term_match: TermMatch, 
    will_remove: bool
) -> float:
    """Calculate confidence score for a cleaning decision.
    
    Args:
        name: The full company name.
        term_match: The matched term.
        will_remove: Whether the term will be removed.
        
    Returns:
        Confidence score between 0.0 and 1.0.
    """
    # Start with base confidence
    confidence = 0.5
    
    # Position-based scoring
    # Check if term is at the end of the name (after the last word)
    words = name.split()
    if words:
        last_word_start = name.rfind(words[-1])
        if term_match.position >= last_word_start:
            # Term is part of or after the last word - high confidence
            confidence = 0.9
        elif len(words) > 2 and term_match.position > name.find(words[-2]):
            # Term is after the second-to-last word - good confidence
            confidence = 0.8
        else:
            # Term is somewhere in the middle or beginning
            confidence = 0.5
    else:
        confidence = 0.5
    
    # Adjust based on term category
    high_confidence_categories = ["corporation", "limited_liability", "limited"]
    if term_match.category in high_confidence_categories:
        confidence += 0.05
    
    # If we're preserving when we normally would remove, lower confidence
    if not will_remove and confidence >= 0.8:
        confidence = min(confidence * 0.7, 0.5)
    
    # Ensure confidence is within bounds
    confidence = max(0.1, min(1.0, confidence))
    
    return round(confidence, 2)


def get_confidence_reasoning(confidence: float, factors: dict[str, Any]) -> str:
    """Generate human-readable explanation of confidence score.
    
    Args:
        confidence: The confidence score.
        factors: Dictionary of factors that influenced the score.
        
    Returns:
        Human-readable reasoning string.
    """
    if confidence >= 0.9:
        level = "high confidence"
    elif confidence >= 0.5:
        level = "medium confidence"
    else:
        level = "low confidence"
    
    reasoning_parts = [f"Cleaning performed with {level} ({confidence})"]
    
    if "position" in factors:
        position = factors["position"]
        if position == "suffix":
            reasoning_parts.append("term appears as a clear suffix")
        elif position == "middle":
            reasoning_parts.append("term appears in the middle of the name")
        elif position == "prefix":
            reasoning_parts.append("term appears at the beginning")
    
    if "preserved" in factors and factors["preserved"]:
        reasoning_parts.append("term was preserved to maintain name integrity")
    
    if "category" in factors:
        reasoning_parts.append(f"term is a {factors['category']} indicator")
    
    return " - ".join(reasoning_parts)


def apply_cleaning_logic(
    original: str,
    normalized: str,
    matches: list[TermMatch],
    config: CleanerConfig
) -> CleaningResult:
    """Apply cleaning logic to generate the final result.
    
    Args:
        original: Original company name
        normalized: Normalized version of the name
        matches: List of term matches found
        config: Configuration settings
        
    Returns:
        CleaningResult with cleaned name and metadata
    """
    # Handle configuration checks
    if not config.remove_corporate_suffixes:
        return CleaningResult(
            original=original,
            cleaned=original,
            confidence=1.0,
            confidence_level="high",
            changes_made=False,
            reason="Corporate suffix removal is disabled"
        )
    
    # If no matches found, return original
    if not matches:
        return CleaningResult(
            original=original,
            cleaned=original,
            confidence=0.95,
            confidence_level="high", 
            changes_made=False,
            reason="No corporate suffixes found"
        )
    
    # Sort matches by position (rightmost first)
    matches_sorted = sorted(matches, key=lambda m: m.position, reverse=True)
    
    cleaned = original
    changes_made = False
    preserved_terms = []
    removed_terms = []
    confidence_scores = []
    
    for match in matches_sorted:
        # Calculate remaining words after potential removal
        words_before_removal = len(cleaned.split())
        potential_cleaned = cleaned[:match.position].strip()
        remaining_words = len(potential_cleaned.split()) if potential_cleaned else 0
        
        # Check if we should preserve this term
        should_preserve = False
        preserve_reason = ""
        
        if config.preserve_known_brands:
            should_preserve, preserve_reason = should_preserve_term(
                original, match, remaining_words
            )
        
        # Calculate confidence for this decision
        confidence = calculate_confidence(original, match, not should_preserve)
        confidence_scores.append(confidence)
        
        if should_preserve:
            preserved_terms.append(f"{match.term} ({preserve_reason})")
        else:
            # Remove the term
            cleaned = cleaned[:match.position].strip()
            # Remove trailing punctuation like commas
            if cleaned.endswith(','):
                cleaned = cleaned[:-1].strip()
            removed_terms.append(match.term)
            changes_made = True
    
    # Calculate overall confidence
    overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.95
    
    # Determine confidence level
    if overall_confidence >= 0.8:
        confidence_level = "high"
    elif overall_confidence >= 0.5:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    # Build reason string
    reason_parts = []
    if removed_terms:
        reason_parts.append(f"Removed: {', '.join(removed_terms)}")
    if preserved_terms:
        reason_parts.append(f"Preserved: {'; '.join(preserved_terms)}")
    if not changes_made:
        reason_parts.append("No changes made")
        
    reason = " | ".join(reason_parts) if reason_parts else "Processing complete"
    
    return CleaningResult(
        original=original,
        cleaned=cleaned,
        confidence=round(overall_confidence, 2),
        confidence_level=confidence_level,
        changes_made=changes_made,
        reason=reason
    )