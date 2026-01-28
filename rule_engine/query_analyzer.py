# rule_engine/query_analyzer.py

import re

def should_skip_rules(query: str, max_tokens: int = 12) -> bool:
    """
    Decide whether to skip rule engine and go directly to ML.
    Rules are valuable for short & ambiguous queries.
    
    Skips rules for:
    - Empty input
    - Very long queries (> max_tokens)
    - Conversational/narrative input
    
    Args:
        query: User input query
        max_tokens: Maximum token threshold for rule engine
    
    Returns:
        bool: True if should skip rules, False otherwise
    """
    
    tokens = query.strip().lower().split()
    
    # Empty input → skip
    if not tokens:
        return True
    
    # Very long queries → skip rules (they're likely natural conversations)
    if len(tokens) > max_tokens:
        return True
    
    # Otherwise ALWAYS allow rules for short queries
    return False


def analyze_query_characteristics(query: str) -> dict:
    """
    Analyzes query characteristics for routing decisions.
    
    Args:
        query: User input query
    
    Returns:
        dict: Analysis results including length, intent signals, etc.
    """
    tokens = query.strip().lower().split()
    
    analysis = {
        "original_query": query,
        "token_count": len(tokens),
        "char_count": len(query),
        "is_question": query.strip().endswith('?'),
        "is_command": query.strip().startswith(('help', 'show', 'get', 'list', 'find')),
        "is_affirmation": _is_affirmation(query),
        "is_negation": _is_negation(query),
        "has_pricing_keyword": _has_keyword(query, ['price', 'pricing', 'cost', 'expense']),
        "has_demo_keyword": _has_keyword(query, ['demo', 'demonstration', 'walkthrough', 'example']),
        "has_support_keyword": _has_keyword(query, ['help', 'support', 'assist', 'problem', 'issue']),
        "has_contact_keyword": _has_keyword(query, ['contact', 'reach', 'call', 'email', 'phone']),
        "has_trial_keyword": _has_keyword(query, ['trial', 'try', 'test', 'free']),
    }
    
    return analysis


def _is_affirmation(query: str) -> bool:
    """Checks if query is an affirmation."""
    affirmations = ['yes', 'yeah', 'sure', 'ok', 'okay', 'agree', 'confirmed', 'affirmative']
    return any(aff in query.lower() for aff in affirmations)


def _is_negation(query: str) -> bool:
    """Checks if query is a negation."""
    negations = ['no', 'nope', 'not', 'deny', 'denied', 'negative', 'declined']
    return any(neg in query.lower() for neg in negations)


def _has_keyword(query: str, keywords: list) -> bool:
    """Checks if query contains any of the given keywords."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in keywords)


def get_query_intent_category(analysis: dict) -> str:
    """
    Determines the intent category from query analysis.
    
    Args:
        analysis: Query analysis dictionary from analyze_query_characteristics
    
    Returns:
        str: Estimated intent category ('pricing', 'demo', 'support', 'sales', 'unknown')
    """
    
    if analysis.get("has_pricing_keyword"):
        return "pricing_inquiry"
    elif analysis.get("has_demo_keyword"):
        return "demo_request"
    elif analysis.get("has_support_keyword"):
        return "technical_support"
    elif analysis.get("has_contact_keyword"):
        return "sales_contact_request"
    elif analysis.get("has_trial_keyword"):
        return "free_trial_request"
    
    return "unknown"

