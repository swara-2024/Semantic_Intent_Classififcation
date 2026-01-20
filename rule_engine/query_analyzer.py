# rule_engine/query_analyzer.py

BUSINESS_VERBS = {
    "want", "need", "looking", "explore", "planning",
    "interested", "searching"
}

BUSINESS_NOUNS = {
    "service", "services", "product", "platform",
    "pricing", "solution", "internship", "job",
    "career", "demo", "trial"
}

def should_skip_rules(query: str, max_tokens: int = 3) -> bool:
    """
    Returns True if rule engine should be skipped
    and query should go directly to ML.
    """
    tokens = query.lower().split()

    # Length guard
    if len(tokens) > max_tokens:
        return True

    # Mixed intent guard (verb + business noun)
    has_verb = any(t in BUSINESS_VERBS for t in tokens)
    has_noun = any(t in BUSINESS_NOUNS for t in tokens)

    if has_verb and has_noun:
        return True

    return False
