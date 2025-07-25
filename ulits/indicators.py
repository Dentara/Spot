import pandas as pd

def calculate_ema(prices: list[float], period: int) -> float:
    if len(prices) < period:
        raise ValueError("Yetərli qədər data yoxdur EMA üçün")
    series = pd.Series(prices)
    ema = series.ewm(span=period, adjust=False).mean()
    return round(ema.iloc[-1], 4)

def calculate_rsi(prices: list[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        raise ValueError("Yetərli qədər data yoxdur RSI üçün")

    series = pd.Series(prices)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)
