from ulits.indicators import calculate_ema, calculate_rsi
from ai.trend_detector import TrendDetector
from ai.pattern_recognizer import detect_pattern

class SpotManager:
    def __init__(self):
        self.ema_fast = 7
        self.ema_slow = 21
        self.rsi_period = 14
        self.trend_detector = TrendDetector()

    def get_indicators(self, close_prices):
        ema7 = calculate_ema(close_prices, self.ema_fast)
        ema21 = calculate_ema(close_prices, self.ema_slow)
        rsi = calculate_rsi(close_prices, self.rsi_period)
        return {
            "ema7": ema7,
            "ema21": ema21,
            "rsi": rsi
        }

    def get_trend(self, close_prices):
        return self.trend_detector.detect_trend(close_prices)

    def get_pattern(self, candles):
        return detect_pattern(candles)

    def create_prompt(self, symbol, indicators, trend, pattern, price):
        return (
            f"{symbol} üçün texniki analiz:\n"
            f"EMA7: {indicators['ema7']}, EMA21: {indicators['ema21']}, RSI: {indicators['rsi']},\n"
            f"Trend: {trend}, Pattern: {pattern}, Qiymət: {price}\n"
            f"Yalnız bir cavab ver: BUY, SELL və ya NO_ACTION. Əlavə heç nə yazma."
            f"Əlavə şərh və ya izah vermə. Sadəcə qərarı bildir."
        )
