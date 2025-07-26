import json
import os

MEMORY_PATH = "stats/strategy_memory.json"

class Tracker:
    def __init__(self):
        os.makedirs("stats", exist_ok=True)
        if not os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "w") as f:
                json.dump({}, f)

    def update(self, symbol, side, prev_amount, current_amount):
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)

        symbol_key = symbol.replace("/", "_")
        if symbol_key not in memory:
            memory[symbol_key] = {
                "BUY": {"success": 0, "fail": 0},
                "SELL": {"success": 0, "fail": 0}
            }

        result = "fail"
        if side == "BUY" and current_amount > prev_amount:
            result = "success"
        elif side == "SELL" and current_amount < prev_amount:
            result = "success"

        memory[symbol_key][side][result] += 1

        with open(MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)

    def get_stats(self, symbol):
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
        symbol_key = symbol.replace("/", "_")
        return memory.get(symbol_key, {})
