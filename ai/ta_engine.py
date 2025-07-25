# ai/ta_engine.py

import numpy as np

def calculate_rsi(closes, period=14):
    closes = np.array(closes)
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ema(closes, period):
    closes = np.array(closes)
    k = 2 / (period + 1)
    ema = [closes[0]]
    for price in closes[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema[-1]

def analyze_technicals(candles):
    closes = [x[4] for x in candles]
    if len(closes) < 21:
        return "hold"

    rsi = calculate_rsi(closes)
    ema_short = calculate_ema(closes, 9)
    ema_long = calculate_ema(closes, 21)

    if rsi < 35 and ema_short > ema_long:
        return "buy"
    elif rsi > 65 and ema_short < ema_long:
        return "sell"
    return "hold"
