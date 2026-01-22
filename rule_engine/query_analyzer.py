# rule_engine/query_analyzer.py

def should_skip_rules(query: str, max_tokens: int = 12) -> bool:
    """
    Decide whether to skip rule engine and go directly to ML.
    Rules are valuable for short & ambiguous queries.
    """

    tokens = query.strip().lower().split()

    # Empty input → skip
    if not tokens:
        return True

    # Very long queries → skip rules
    if len(tokens) > max_tokens:
        return True

    # Otherwise ALWAYS allow rules
    return False
