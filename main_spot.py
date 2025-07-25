import os
import time
import ccxt
import json
from datetime import datetime
from ai.spot_manager import SpotManager
from ulits.spot_trade_executor import execute_spot_trade
from ai.gpt_assistant import ask_gpt
from ulits.telegram_notifier import send_telegram_message

# === GATE.IO bağlantısı
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
})

# === Token siyahısı
TOKENS = [
    "TON/USDT", "DBC/USDT", "DENT/USDT", "WIFI/USDT", "ADA/USDT",
    "CFG/USDT", "LTO/USDT", "GT/USDT", "KAS/USDT", "XRD/USDT"
]

manager = SpotManager()
last_sold_amounts = {}
last_sold_timestamps = {}

TRADE_LOG_DIR = "logs"
os.makedirs(TRADE_LOG_DIR, exist_ok=True)

def log_trade(symbol, side, amount, price):
    symbol_name = symbol.replace("/", "_")
    path = os.path.join(TRADE_LOG_DIR, f"{symbol_name}.json")
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "side": side,
        "amount": amount,
        "price": price
    }

    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        send_telegram_message(f"⚠️ Log yazıla bilmədi ({symbol}): {e}")

def run():
    send_telegram_message("✅ SPOT BOT AKTİVDİR – Plan üzrə ticarətə başlayır")

    while True:
        for symbol in TOKENS:
            try:
                send_telegram_message(f"🔄 {symbol} üçün analiz başlayır")

                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
                close_prices = [x[4] for x in ohlcv]
                price = close_prices[-1]
                indicators = manager.get_indicators(close_prices)
                pattern = manager.get_pattern(ohlcv)
                trend = manager.get_trend(close_prices)

                gpt_msg = manager.create_prompt(symbol, indicators, trend, pattern, price)
                gpt_raw = ask_gpt(gpt_msg)
                gpt_decision = gpt_raw.strip().upper()
                decision = gpt_decision  # ✅ SƏHVLƏRİ HƏLL EDİR

                send_telegram_message(f"🤖 GPT cavabı ({symbol}): <code>{gpt_raw}</code>")

                if decision not in ["BUY", "SELL"]:
                    send_telegram_message(f"📍 Qərar: NO_ACTION ({symbol})")
                    continue

                balance = exchange.fetch_balance()
                free_usdt = balance['free'].get('USDT', 0)
                token_name = symbol.split('/')[0]
                token_balance = balance['free'].get(token_name, 0)

                now = time.time()

                # === SELL
                if decision == "SELL" and token_balance >= 1:
                    sell_amount = round(token_balance * 0.05, 2)
                    if sell_amount < 1:
                        continue

                    order = exchange.create_order(symbol, 'market', 'sell', sell_amount)
                    usdt_gained = sell_amount * price
                    last_sold_amounts[symbol] = {
                        "usdt": usdt_gained,
                        "token": sell_amount,
                        "price": price
                    }
                    last_sold_timestamps[symbol] = now
                    send_telegram_message(f"📉 SELL: {symbol} | {sell_amount}")
                    log_trade(symbol, "SELL", sell_amount, price)
                    continue

                # === BUY
                if decision == "BUY":
                    if symbol in last_sold_timestamps and now - last_sold_timestamps[symbol] < 600:
                        send_telegram_message(f"⏳ {symbol} üçün cooldown aktivdir")
                        continue

                    if symbol in last_sold_amounts:
                        buy_usdt = last_sold_amounts[symbol]["usdt"]
                        prev_token_qty = last_sold_amounts[symbol]["token"]
                    else:
                        buy_usdt = free_usdt * 0.05
                        prev_token_qty = 0

                    if buy_usdt < 1:
                        continue

                    buy_amount = round(buy_usdt / price, 2)
                    if prev_token_qty > 0 and buy_amount <= prev_token_qty:
                        send_telegram_message(f"⚠️ {symbol}: Yeni alınan say əvvəlkindən azdır ({buy_amount} ≤ {prev_token_qty})")
                        continue

                    order = exchange.create_order(symbol, 'market', 'buy', buy_amount, price)  # ✅ Gate.io tələb edir
                    send_telegram_message(f"📈 BUY: {symbol} | {buy_amount}")
                    log_trade(symbol, "BUY", buy_amount, price)
                    continue

            except Exception as e:
                send_telegram_message(f"❌ {symbol} üçün xəta: {e}")
                continue

        time.sleep(60)

run()