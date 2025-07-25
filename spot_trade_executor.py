from datetime import datetime
import time

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def execute_spot_trade(exchange, symbol: str, side: str, amount: float) -> dict:
    try:
        log(f"📤 Spot əməliyyat siqnalı: {side.upper()} göndərilir – {symbol} | {amount}")

        if side == "BUY":
            order = exchange.create_market_buy_order(symbol, amount)
        elif side == "SELL":
            order = exchange.create_market_sell_order(symbol, amount)
        else:
            log(f"❌ Naməlum əməliyyat tipi: {side}")
            return {}

        log(f"✅ {side.upper()} əmri uğurla icra edildi: {symbol} | {amount}")
        return order

    except Exception as e:
        log(f"❗ Spot əməliyyat xətası: {e}")
        time.sleep(5)
        return {}
