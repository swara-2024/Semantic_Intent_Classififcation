# rule_engine/rule_loader.py

import yaml
import re

def load_rules(yaml_paths):
    """
    yaml_paths: list of rule yaml file paths
    """
    rules = []

    for path in yaml_paths:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or []
            rules.extend(data)

    # Compile regex patterns once
    for rule in rules:
        compiled = []
        for pattern in rule.get("match", {}).get("regex", []):
            compiled.append(re.compile(pattern, re.IGNORECASE))
        rule["_compiled_regex"] = compiled

    # Sort by priority (lower = higher priority)
    rules.sort(key=lambda r: r.get("priority", 100))
    return rules
