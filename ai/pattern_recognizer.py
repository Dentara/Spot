# ai/pattern_recognizer.py

import numpy as np

def detect_pattern(candles):
    opens = np.array([x[1] for x in candles])
    highs = np.array([x[2] for x in candles])
    lows = np.array([x[3] for x in candles])
    closes = np.array([x[4] for x in candles])

    last_open = opens[-1]
    last_close = closes[-1]
    last_high = highs[-1]
    last_low = lows[-1]

    body_size = abs(last_close - last_open)
    candle_range = last_high - last_low
    upper_shadow = last_high - max(last_close, last_open)
    lower_shadow = min(last_close, last_open) - last_low

    if candle_range == 0:
        return "neutral"

    body_ratio = body_size / candle_range
    lower_shadow_ratio = lower_shadow / candle_range
    upper_shadow_ratio = upper_shadow / candle_range

    if body_ratio < 0.3 and lower_shadow_ratio > 0.5:
        return "bullish"
    elif body_ratio < 0.3 and upper_shadow_ratio > 0.5:
        return "bearish"
    else:
        return "neutral"
