import os
import time
import ccxt
import json
from datetime import datetime
from ai.spot_manager import SpotManager
from ulits.spot_trade_executor import execute_spot_trade
from ai.gpt_assistant import ask_gpt
from ulits.telegram_notifier import send_telegram_message
from ai.ta_engine import analyze_technicals
from ai.reinforcement_tracker import Tracker  # ✅ yeni modul daxil edildi

# === Telegram səviyyə kontrolu
DEBUG_MODE = False

def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    if level == "silent":
        return
    send_telegram_message(msg)

# === GATE.IO bağlantısı
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
})

TOKENS = [
    "TON/USDT", "DBC/USDT", "DENT/USDT", "WIFI/USDT", "ADA/USDT",
    "CFG/USDT", "LTO/USDT", "GT/USDT", "KAS/USDT", "XRD/USDT", "XRP/USDT"
]

manager = SpotManager()
tracker = Tracker()  # ✅ reinforcement izləyicisi yaradılır
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
        notify(f"⚠️ Log yazıla bilmədi ({symbol}): {e}", level="debug")

def run():
    notify("✅ SPOT BOT AKTİVDİR – reinforcement tracker aktivdir", level="info")

    while True:
        for symbol in TOKENS:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
                ohlcv_1h = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=30)
                ohlcv_4h = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=30)

                close_prices = [x[4] for x in ohlcv]
                price = close_prices[-1]
                indicators = manager.get_indicators(close_prices)
                pattern = manager.get_pattern(ohlcv)
                trend = manager.get_trend(close_prices)

                trend_1h = analyze_technicals(ohlcv_1h)
                trend_4h = analyze_technicals(ohlcv_4h)

                gpt_msg = manager.create_prompt(symbol, indicators, trend, pattern, price)
                gpt_raw = ask_gpt(gpt_msg)
                gpt_decision = gpt_raw.strip().upper()
                decision = gpt_decision

                if decision not in ["BUY", "SELL"]:
                    notify(f"📍 Qərar: NO_ACTION ({symbol})", level="debug")
                    continue

                balance = exchange.fetch_balance()
                free_usdt = balance['free'].get('USDT', 0)
                token_name = symbol.split('/')[0]
                token_balance = balance['free'].get(token_name, 0)
                now = time.time()

                if decision == "SELL" and (trend_1h == "buy" or trend_4h == "buy"):
                    notify(f"⛔ {symbol}: 1h və 4h artım trendindədir, SATIŞ BLOKLANDI")
                    continue

                if decision == "BUY" and (trend_1h == "sell" and trend_4h == "sell"):
                    notify(f"⚠️ {symbol}: 1h və 4h düşüş trendindədir, ALIŞ BLOKLANDI")
                    continue

                # === SELL cooldown
                if decision == "SELL":
                    if symbol in last_sold_timestamps and now - last_sold_timestamps[symbol] < 1800:
                        notify(f"⏳ {symbol} üçün SELL cooldown aktivdir", level="silent")
                        continue

                    if token_balance >= 1:
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
                        tracker.update(symbol, "SELL", token_balance, token_balance - sell_amount)  # ✅ izləmə
                        notify(f"📉 SELL: {symbol} | {sell_amount}")
                        log_trade(symbol, "SELL", sell_amount, price)
                        continue

                # === BUY
                if decision == "BUY":
                    if symbol in last_sold_amounts:
                        buy_usdt = last_sold_amounts[symbol]["usdt"]
                        prev_token_qty = last_sold_amounts[symbol]["token"]
                        prev_price = last_sold_amounts[symbol]["price"]
                    else:
                        buy_usdt = free_usdt * 0.05
                        prev_token_qty = 0
                        prev_price = price

                    if buy_usdt < 1:
                        continue

                    buy_amount = round(buy_usdt / price, 2)

                    if prev_token_qty > 0 and buy_amount <= prev_token_qty:
                        notify(f"⚠️ {symbol}: Yeni alınan say əvvəlkindən azdır ({buy_amount} ≤ {prev_token_qty})")
                        continue

                    if prev_price > 0 and price >= prev_price:
                        notify(f"⚠️ {symbol}: Qiymət əvvəlkindən ucuz deyil ({price:.6f} ≥ {prev_price:.6f})")
                        continue

                    skip_gain_check = trend_1h == "buy" or trend_4h == "buy"
                    percent_gain = ((buy_amount - prev_token_qty) / prev_token_qty) * 100 if prev_token_qty > 0 else 100

                    if not skip_gain_check and percent_gain < 2:
                        notify(f"⚠️ {symbol}: Say fərqi çox azdır ({percent_gain:.2f}%)")
                        continue

                    order = exchange.create_order(symbol, 'market', 'buy', buy_amount, price)
                    tracker.update(symbol, "BUY", prev_token_qty, buy_amount)  # ✅ izləmə
                    notify(f"📈 BUY: {symbol} | {buy_amount} ({percent_gain:.2f}% artım)")
                    log_trade(symbol, "BUY", buy_amount, price)
                    continue

            except Exception as e:
                notify(f"❌ {symbol} üçün xəta: {e}", level="info")
                continue

        time.sleep(60)

run()
