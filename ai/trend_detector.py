# ai/trend_detector.py

class TrendDetector:
    def __init__(self, candle_count: int = 5):
        self.candle_count = candle_count

    def detect_trend(self, close_prices: list[float]) -> str:
        if len(close_prices) < self.candle_count:
            return \"neutral\"

        recent = close_prices[-self.candle_count:]
        up = all(recent[i] < recent[i + 1] for i in range(len(recent) - 1))
        down = all(recent[i] > recent[i + 1] for i in range(len(recent) - 1))

        if up:
            return \"uptrend\"
        elif down:
            return \"downtrend\"
        else:
            return \"range\"
