# rule_engine/rule_pipeline.py

from rule_engine.rule_loader import load_rules
from rule_engine.rule_engine import RuleEngine
from rule_engine.query_analyzer import should_skip_rules

class RulePipeline:
    def __init__(self, rule_files: list[str]):
        rules = load_rules(rule_files)
        self.engine = RuleEngine(rules)

    def run(self, query: str) -> dict:
        # 🚀 Pre-rule gate (most important)
        if should_skip_rules(query):
            return {
                "matched": False,
                "reason": "SKIPPED_RULE_ENGINE"
            }

        return self.engine.process(query)
