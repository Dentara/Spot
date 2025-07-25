from datetime import datetime
import time

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def execute_spot_trade(exchange, symbol: str, side: str, amount: float) -> dict:
    try:
        log(f"📤 Əməliyyat siqnalı gəldi: {side.upper()} göndərilir")
        if side == "buy":
            order = exchange.create_market_buy_order(symbol, amount)
        elif side == "sell":
            order = exchange.create_market_sell_order(symbol, amount)
        else:
            log(f"❌ Naməlum əməliyyat növü: {side}")
            return {}
        log(f"✅ {side.upper()} {amount} {symbol} icra edildi")
        return order

    except Exception as e:
        log(f"❗ Əməliyyat xətası: {e}")
        time.sleep(5)
        return {}
