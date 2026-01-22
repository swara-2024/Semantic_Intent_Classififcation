# rule_engine/rule_engine.py

import random
from rule_engine.rule_matcher import rule_matches

class RuleEngine:
    def __init__(self, rules):
        self.rules = rules

    def process(self, query: str) -> dict:
        matched_rules = []
        token_count = len(query.strip().split())  # ✅ ADD THIS

        for rule in self.rules:
            # ✅ ENFORCE max_tokens IF PRESENT
            max_tokens = rule.get("max_tokens")
            if max_tokens is not None and token_count > max_tokens:
                continue

            if rule_matches(rule, query):
                matched_rules.append(rule)

            # Conflict guard (fail fast)
            if len(matched_rules) > 1:
                break

        # ❌ No rule matched
        if not matched_rules:
            return self._fail("NO_RULE_MATCH")

        # ❌ Conflicting rules
        if len(matched_rules) > 1:
            return self._fail("MULTIPLE_RULE_MATCH")

        rule = matched_rules[0]
        response_text = random.choice(rule["response"]["messages"])

        return {
            "matched": True,
            "intent": rule["intent"],
            "confidence": rule.get("confidence", 1.0),
            "response": response_text,
            "allow_ml_fallback": rule.get("allow_ml_fallback", True),
            "reason": "RULE_MATCH"
        }

    def _fail(self, reason: str) -> dict:
        return {
            "matched": False,
            "intent": None,
            "confidence": 0.0,
            "response": None,
            "allow_ml_fallback": True,
            "reason": reason
        }
