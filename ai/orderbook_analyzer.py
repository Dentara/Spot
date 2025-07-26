# ai/orderbook_analyzer.py

def analyze_order_book_depth(order_book: dict, threshold_ratio: float = 2.0) -> str:
    """
    Buy və Sell dərinliklərini analiz edir.
    Əgər tərəflərdən biri çox güclüdürsə və ya total likvidlik azdırsa → risky hesab olunur.
    """
    try:
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])

        if not bids or not asks:
            return "illiquid"

        bid_volume = sum([price * amount for price, amount in bids[:10]])
        ask_volume = sum([price * amount for price, amount in asks[:10]])

        total_volume = bid_volume + ask_volume
        if total_volume < 100:  # 100 USDT-dən az likvidlik varsa
            return "illiquid"

        ratio = max(bid_volume / ask_volume, ask_volume / bid_volume)
        if ratio > threshold_ratio:
            return "risky"

        return "ok"

    except Exception:
        return "illiquid"
