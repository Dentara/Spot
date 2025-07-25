from utils.indicators import calculate_ema, calculate_rsi
from ai.trend_detector import TrendDetector
from ai.pattern_recognizer import detect_pattern

class SpotManager:
    def __init__(self):
        self.trend_detector = TrendDetector()

    def get_indicators(self, close_prices: list[float]) -> dict:
        return {
            "ema_fast": calculate_ema(close_prices, 7),
            "ema_slow": calculate_ema(close_prices, 21),
            "rsi": calculate_rsi(close_prices, 14)
        }

    def get_pattern(self, candles: list[list]) -> str:
        return detect_pattern(candles)

    def get_trend(self, close_prices: list[float]) -> str:
        return self.trend_detector.detect_trend(close_prices)

    def create_prompt(self, symbol: str, indicators: dict, trend: str, pattern: str, price: float) -> str:
        return (
            f"Token: {symbol}\n"
            f"Texniki analiz məlumatları:\n"
            f"EMA(7): {indicators['ema_fast']}, EMA(21): {indicators['ema_slow']}\n"
            f"RSI: {indicators['rsi']}, Trend: {trend}, Pattern: {pattern}\n"
            f"Cari qiymət: {price} USDT\n"
            f"Bütün bu məlumatlara əsaslanaraq yalnız bir sözlə cavab ver: BUY, SELL və ya NO_ACTION.\n"
            f"Əlavə şərh və ya izah vermə. Sadəcə qərarı bildir."
        )
