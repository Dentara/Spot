import os
import time
import ccxt
import json
from datetime import datetime, timezone
from ai.spot_manager import SpotManager
from ulits.spot_trade_executor import execute_spot_trade
from ai.gpt_rich_prompt import ask_gpt_rich
from ulits.telegram_notifier import send_telegram_message
from ai.ta_engine import analyze_technicals
from ai.reinforcement_tracker import Tracker
from ai.sentiment_analyzer import get_sentiment_score
from ai.whale_detector import get_whale_alerts
from ai.orderbook_analyzer import analyze_order_book_depth
from ai.correlation_engine import get_related_tokens
from ai.performance_logger import update_daily_stats

DEBUG_MODE = False

def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    if level == "silent":
        return
    send_telegram_message(msg)

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
tracker = Tracker()
last_buy_prices = {}
last_sold_timestamps = {}
recent_decisions = {}

TRADE_LOG_DIR = "logs"
os.makedirs(TRADE_LOG_DIR, exist_ok=True)

def log_trade(symbol, side, amount, price):
    symbol_name = symbol.replace("/", "_")
    path = os.path.join(TRADE_LOG_DIR, f"{symbol_name}.json")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
    notify("✅ SPOT BOT AKTİVDİR – Ağıllı alış-satış strategiyası ilə", level="info")

    while True:
        for symbol in TOKENS:
            try:
                order_book = exchange.fetch_order_book(symbol)
                depth_status = analyze_order_book_depth(order_book)
                if depth_status != "ok":
                    notify(f"🚫 {symbol}: Order Book zəif ({depth_status})", level="info")
                    continue

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
                gpt_result = ask_gpt_rich(gpt_msg)
                gpt_decision = gpt_result["decision"]
                gpt_reason = gpt_result["explanation"]
                decision = gpt_decision

                notify(f"🤖 GPT qərarı: {gpt_decision}\n{gpt_reason}", level="debug")

                token_name = symbol.split('/')[0]

                sentiment = get_sentiment_score(token_name)
                whale_active = get_whale_alerts(token_name)
                if sentiment == "bearish" or whale_active:
                    notify(f"🚫 {symbol}: Sentiment ({sentiment}) və ya Whale aktivliyi səbəbilə BLOKLANDI", level="info")
                    continue

                related = get_related_tokens(symbol)
                related_buy = any(recent_decisions.get(t) == "BUY" for t in related)
                related_sell = any(recent_decisions.get(t) == "SELL" for t in related)

                if decision == "NO_ACTION" and related_buy:
                    decision = "BUY"
                    notify(f"🔄 {symbol}: NO_ACTION idi, bağlı token BUY verdiyi üçün BUY edilir", level="info")
                elif decision == "NO_ACTION" and related_sell:
                    decision = "SELL"
                    notify(f"🔄 {symbol}: NO_ACTION idi, bağlı token SELL verdiyi üçün SELL edilir", level="info")

                recent_decisions[symbol] = decision

                if decision not in ["BUY", "SELL"]:
                    notify(f"📍 Qərar: NO_ACTION ({symbol})", level="debug")
                    continue

                balance = exchange.fetch_balance()
                free_usdt = balance['free'].get('USDT', 0)
                token_balance = balance['free'].get(token_name, 0)
                now = time.time()
                if decision == "SELL":
                    if token_balance < 1:
                        notify(f"⚠️ {symbol}: Token balansı çox azdır, satış keçildi", level="info")
                        continue

                    if trend_1h != "buy" or trend_4h != "buy":
                        notify(f"⛔ {symbol}: Trend artımda deyil, satış uyğun deyil", level="info")
                        continue

                    last_buy_price = last_buy_prices.get(symbol, 0)
                    profit_threshold = 0.02  # 2% mənfəət

                    if last_buy_price == 0 or price < last_buy_price * (1 + profit_threshold):
                        notify(f"ℹ️ {symbol}: Satış üçün kifayət qədər mənfəət yoxdur ({price:.4f} < {last_buy_price * (1 + profit_threshold):.4f})")
                        continue

                    sell_amount = round(token_balance * 0.05, 2)
                    if sell_amount < 1:
                        continue

                    order = exchange.create_order(symbol, 'market', 'sell', sell_amount)
                    last_sold_timestamps[symbol] = now
                    tracker.update(symbol, "SELL", token_balance, token_balance - sell_amount)
                    notify(f"📉 SELL: {symbol} | {sell_amount}")
                    log_trade(symbol, "SELL", sell_amount, price)

                    if 'info' in order and 'profit' in order['info']:
                        pnl = float(order['info']['profit'])
                        success = pnl >= 0
                        update_daily_stats(symbol, "SELL", success, pnl)
                    continue

                if decision == "BUY":
                    buy_usdt = free_usdt * 0.15  # dinamik alış
                    if trend_1h == "buy" and trend_4h == "buy":
                        buy_usdt = free_usdt * 0.3
                        notify(f"🚀 {symbol}: Güclü trend → alış sərbəstləşdirildi ({buy_usdt:.2f} USDT)", level="info")

                    if buy_usdt < 3:
                        notify(f"⚠️ {symbol}: Alış üçün vəsait çox azdır ({buy_usdt:.2f} USDT < 3)", level="info")
                        continue

                    buy_amount = round(buy_usdt / price, 2)
                    order = exchange.create_order(symbol, 'market', 'buy', buy_amount, price)

                    tracker.update(symbol, "BUY", 0, buy_amount)
                    last_buy_prices[symbol] = price
                    notify(f"📈 BUY: {symbol} | {buy_amount} ({buy_usdt:.2f} USDT)")
                    log_trade(symbol, "BUY", buy_amount, price)

                    if 'info' in order and 'profit' in order['info']:
                        pnl = float(order['info']['profit'])
                        success = pnl >= 0
                        update_daily_stats(symbol, "BUY", success, pnl)
                    continue

            except Exception as e:
                notify(f"❌ {symbol} üçün xəta: {e}", level="info")
                continue

        time.sleep(60)

run()
