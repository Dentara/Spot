# ai/performance_logger.py

import os
import json
from datetime import datetime, timezone

PERF_PATH = "stats/performance.json"
TOKEN_LOG_DIR = "stats/token_logs"
os.makedirs(TOKEN_LOG_DIR, exist_ok=True)

def update_daily_stats(symbol: str, side: str, success: bool, pnl: float):
    today = datetime.now(timezone.utc).date().isoformat()
    data = {}

    if os.path.exists(PERF_PATH):
        with open(PERF_PATH, "r") as f:
            data = json.load(f)

    if today not in data:
        data[today] = {
            "total_trades": 0,
            "buy": 0,
            "sell": 0,
            "success": 0,
            "fail": 0,
            "net_pnl": 0.0
        }

    day = data[today]
    day["total_trades"] += 1
    day[side.lower()] += 1
    if success:
        day["success"] += 1
    else:
        day["fail"] += 1
    day["net_pnl"] += round(pnl, 3)

    with open(PERF_PATH, "w") as f:
        json.dump(data, f, indent=2)

    log_token_trade(symbol, side, success, pnl)

def log_token_trade(symbol: str, side: str, success: bool, pnl: float):
    file = os.path.join(TOKEN_LOG_DIR, f"{symbol.replace('/', '_')}.json")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "side": side,
        "success": success,
        "pnl": round(pnl, 3)
    }

    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass
