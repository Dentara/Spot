# ai/correlation_engine.py

import json

CORRELATION_FILE = "stats/correlation_matrix.json"

def load_correlation_matrix():
    try:
        with open(CORRELATION_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def get_related_tokens(symbol: str) -> list:
    matrix = load_correlation_matrix()
    return matrix.get(symbol, [])
