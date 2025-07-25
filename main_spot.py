import os
import time
import ccxt
from datetime import datetime
from ai.spot_manager import SpotManager
from utils.spot_trade_executor import execute_spot_trade
from ai.gpt_assistant import ask_gpt
from utils.telegram_notifier import send_telegram_message

# === ENV
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    print("❌ API açarları tapılmadı!")
    exit(1)

exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
})

# === TOKENLƏR
TOKENS = ["DBC/USDT", "DENT/USDT", "WIFI/USDT", "ADA/USDT"]
manager = SpotManager()

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def run():
    log("🚀 SPOT BOT BAŞLADI")

    while True:
        for symbol in TOKENS:
            try:
                # === Candle-ləri çək
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
                close_prices = [x[4] for x in ohlcv]
                price = close_prices[-1]

                # === Texniki analiz və sentiment
                indicators = manager.get_indicators(close_prices)
                pattern = manager.get_pattern(ohlcv)
                trend = manager.get_trend(close_prices)

                # === GPT üçün prompt hazırla və qərarı al
                gpt_msg = manager.create_prompt(symbol, indicators, trend, pattern, price)
                decision = ask_gpt(gpt_msg).strip().upper()

                if decision not in ["BUY", "SELL"]:
                    continue

                # === Balansı yoxla
                balance = exchange.fetch_balance()
                free_usdt = balance['free']['USDT']
                amount = round((free_usdt * 0.03) / price, 2)
                if amount <= 0:
                    continue

                # === Əməliyyatı icra et
                order = execute_spot_trade(exchange, symbol, decision, amount)
                if order:
                    send_telegram_message(f"📍 <b>{symbol}</b> üçün əməliyyat: <b>{decision}</b> | {amount} | Qiymət: {price}")

            except Exception as e:
                log(f"❌ Xəta: {symbol} | {e}")
                continue

        time.sleep(60)

run()
