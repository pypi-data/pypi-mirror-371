"""Term definitions and management for company name cleaning."""

from .types import TermMatch


# Term categories
CORPORATION_TERMS = [
    "company", "incorporated", "corporation", 
    "corp.", "corp", "inc.", "inc", "& co.", "& co"
]

LIMITED_TERMS = [
    "limited", "ltd.", "ltd", "unlimited", "unltd", "ultd", "co.", "co"
]

LLC_TERMS = [
    "llc", "l.l.c.", "plc", "p.l.c."
]

PARTNERSHIP_TERMS = [
    "partnership", "partners", "lp", "l.p.", "llp", "l.l.p."
]

PROFESSIONAL_TERMS = [
    "professional corporation", "p.c.", "pc"
]

INTERNATIONAL_TERMS = [
    "gmbh", "ag", "sa", "s.a.", "nv", "n.v.", "bv", "b.v.", "srl", "spa"
]


def get_all_terms() -> list[str]:
    """Get all terms from all categories.
    
    Returns:
        List of all terms across all categories.
    """
    all_terms = []
    all_terms.extend(CORPORATION_TERMS)
    all_terms.extend(LIMITED_TERMS)
    all_terms.extend(LLC_TERMS)
    all_terms.extend(PARTNERSHIP_TERMS)
    all_terms.extend(PROFESSIONAL_TERMS)
    all_terms.extend(INTERNATIONAL_TERMS)
    return all_terms


def normalize_term(term: str) -> str:
    """Normalize a term for comparison.
    
    Converts to lowercase, removes internal spaces and punctuation.
    
    Args:
        term: The term to normalize.
        
    Returns:
        Normalized term string.
    """
    # Convert to lowercase
    normalized = term.lower()
    
    # Remove all punctuation except '&'
    chars = []
    for char in normalized:
        if char.isalnum() or char == '&':
            chars.append(char)
        elif char == ' ':
            # Skip spaces
            continue
    
    return ''.join(chars)


def get_term_variations(term: str) -> list[str]:
    """Generate common variations of a term.
    
    Creates variations with and without dots, spaces, etc.
    
    Args:
        term: The base term.
        
    Returns:
        List of term variations including the original.
    """
    variations = [term]
    
    # Add lowercase version
    lowercase = term.lower()
    if lowercase != term:
        variations.append(lowercase)
    
    # Add uppercase version
    uppercase = term.upper()
    if uppercase != term and uppercase != lowercase:
        variations.append(uppercase)
    
    # For abbreviations with dots, add version without dots
    if '.' in term:
        no_dots = term.replace('.', '')
        variations.append(no_dots)
        variations.append(no_dots.lower())
        variations.append(no_dots.upper())
    
    # For multi-word terms, add version without spaces
    if ' ' in term:
        no_spaces = term.replace(' ', '')
        variations.append(no_spaces)
        variations.append(no_spaces.lower())
        variations.append(no_spaces.upper())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for v in variations:
        if v not in seen:
            seen.add(v)
            unique_variations.append(v)
    
    return unique_variations


def find_terms_in_name(name: str) -> list[TermMatch]:
    """Find all matching terms in a company name.
    
    Searches for all terms and their variations in the name,
    tracking position and category information.
    
    Args:
        name: The company name to search.
        
    Returns:
        List of TermMatch objects for each found term.
    """
    matches = []
    name_lower = name.lower()
    
    # Define term categories for matching
    term_categories = [
        ("corporation", CORPORATION_TERMS),
        ("limited", LIMITED_TERMS),
        ("limited_liability", LLC_TERMS),
        ("partnership", PARTNERSHIP_TERMS),
        ("professional", PROFESSIONAL_TERMS),
        ("international", INTERNATIONAL_TERMS),
    ]
    
    for category, terms in term_categories:
        for term in terms:
            # Get all variations of the term
            variations = get_term_variations(term)
            
            for variation in variations:
                # Search for the variation in the name
                search_pos = 0
                variation_lower = variation.lower()
                
                while True:
                    pos = name_lower.find(variation_lower, search_pos)
                    if pos == -1:
                        break
                    
                    # Check word boundaries
                    if _is_word_boundary_match(name, pos, len(variation)):
                        # Extract the actual term as it appears in the name
                        actual_term = name[pos:pos + len(variation)]
                        
                        match = TermMatch(
                            term=actual_term,
                            position=pos,
                            category=category,
                            normalized_term=normalize_term(term)
                        )
                        matches.append(match)
                    
                    search_pos = pos + 1
    
    # Remove duplicate matches at the same position
    unique_matches = []
    seen_positions = set()
    
    for match in matches:
        match_key = (match.position, match.normalized_term)
        if match_key not in seen_positions:
            seen_positions.add(match_key)
            unique_matches.append(match)
    
    # Sort by position
    unique_matches.sort(key=lambda m: m.position)
    
    return unique_matches


def _is_word_boundary_match(text: str, start: int, length: int) -> bool:
    """Check if a match at the given position has proper word boundaries.
    
    Args:
        text: The full text.
        start: Start position of the match.
        length: Length of the match.
        
    Returns:
        True if the match has proper word boundaries.
    """
    end = start + length
    
    # Check character before match (if not at start)
    if start > 0:
        char_before = text[start - 1]
        # Allow space, punctuation, or start of string
        if char_before.isalnum():
            # Exception for '&' which can be part of "& co"
            if char_before != '&' and text[start:end].lower() not in ['co', 'co.']:
                return False
    
    # Check character after match (if not at end)
    if end < len(text):
        char_after = text[end]
        # Allow space, punctuation, or end of string
        if char_after.isalnum():
            return False
    
    return True