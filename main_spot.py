import os
import sys
import time
import ccxt
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "ai"))
sys.path.append(os.path.join(BASE_DIR, "ulits"))

from ai.spot_manager import SpotManager
from ulits.spot_trade_executor import execute_spot_trade
from ai.gpt_assistant import ask_gpt
from ulits.telegram_notifier import send_telegram_message

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

TOKENS = [
    "TON/USDT", "DBC/USDT", "ADA/USDT", "DENT/USDT", "WIFI/USDT",
    "CFG/USDT", "LTO/USDT", "GT/USDT", "KAS/USDT", "XRD/USDT"
]
manager = SpotManager()

# Token başına son satılan miqdarı yadda saxlamaq üçün
last_sold_amounts = {}

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def run():
    log("🚀 SPOT BOT BAŞLADI")
    send_telegram_message("✅ SPOT BOT AKTİVDİR – əməliyyata başladı")

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
                decision = ask_gpt(gpt_msg).strip().upper()

                if decision not in ["BUY", "SELL"]:
                    send_telegram_message(f"📍 Qərar: {decision}")
                    continue

                balance = exchange.fetch_balance()
                free_usdt = balance['free'].get('USDT', 0)
                token_name = symbol.split('/')[0]
                token_balance = balance['free'].get(token_name, 0)

                order = None

                if decision == "SELL" and token_balance > 0:
                    sell_amount = round(token_balance * 0.05, 2)
                    if sell_amount >= 1:
                        order = exchange.create_market_sell_order(symbol, sell_amount)
                        last_sold_amounts[symbol] = round(sell_amount * price, 2)
                        send_telegram_message(f"📉 SELL: {symbol} | {sell_amount} | Təxmini gəlir: {last_sold_amounts[symbol]} USDT")

                elif decision == "BUY" and free_usdt > 0:
                    usdt_to_use = last_sold_amounts.get(symbol, free_usdt * 0.05)
                    buy_amount = round(usdt_to_use / price, 2)
                    if buy_amount >= 1:
                        order = exchange.create_market_buy_order(symbol, buy_amount)
                        send_telegram_message(f"📈 BUY: {symbol} | {buy_amount} | Xərclənən: {usdt_to_use} USDT")

                if order:
                    send_telegram_message(f"✅ Əməliyyat icra edildi: {symbol} | {decision}")

            except Exception as e:
                log(f"❌ Xəta: {symbol} | {e}")
                send_telegram_message(f"⚠️ Xəta: {symbol} üçün analizdə problem: {e}")
                continue

        time.sleep(60)

run()
