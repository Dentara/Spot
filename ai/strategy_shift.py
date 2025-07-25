# ai/strategy_shift.py

def determine_strategy(ta_signal, pattern_signal):
    if ta_signal == "buy" and pattern_signal == "bullish":
        return "buy"
    elif ta_signal == "sell" and pattern_signal == "bearish":
        return "sell"
    return "hold"
