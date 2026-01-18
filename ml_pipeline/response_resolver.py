import yaml
import random

class ResponseResolver:
    def __init__(self, path):
        with open(path, "r") as f:
            self.responses = yaml.safe_load(f)

    def resolve(self, intent):
        block = self.responses.get(intent)
        if not block:
            return None
        return random.choice(block["messages"])
