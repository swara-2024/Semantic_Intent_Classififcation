# rule_engine/rule_matcher.py

def rule_matches(rule: dict, query: str) -> bool:
    text = query.lower()
    tokens = text.split()

    # 1️⃣ Negative keyword guard
    for neg in rule.get("negative_keywords", []):
        if neg in text:
            return False

    # 2️⃣ Token length guard (rule-specific)
    max_tokens = rule.get("max_tokens")
    if max_tokens and len(tokens) > max_tokens:
        return False

    # 3️⃣ Regex matching (STRICT)
    for regex in rule.get("_compiled_regex", []):
        if regex.search(text):
            return True

    return False
