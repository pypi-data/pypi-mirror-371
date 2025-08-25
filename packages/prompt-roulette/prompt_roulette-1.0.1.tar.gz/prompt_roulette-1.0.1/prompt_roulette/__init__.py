import json
import random
import os

def prompt_roulette():
    try:
        statements_path = os.path.join(os.path.dirname(__file__), '..', '..', 'statements.json')
        with open(statements_path, 'r') as f:
            statements = json.load(f)
        
        if random.randint(1, 100) == 1:
            return random.choice(statements)
        return ""
    except Exception:
        return ""

__version__ = "1.0.1"
__all__ = ["prompt_roulette"]