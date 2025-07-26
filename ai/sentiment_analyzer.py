# ai/sentiment_analyzer.py

import requests

def get_sentiment_score(token: str = "TON") -> str:
    """
    Sadə sentiment analizi: Cryptopanic vasitəsilə.
    Gələcəkdə LunarCrush və ya GNews API ilə əvəzlənə bilər.
    """
    try:
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies={token}"
        response = requests.get(url)
        data = response.json()

        positive = sum(1 for post in data['results'] if post['vote']['positive'] > 0)
        negative = sum(1 for post in data['results'] if post['vote']['negative'] > 0)

        score = positive - negative

        if score >= 2:
            return "bullish"
        elif score <= -2:
            return "bearish"
        else:
            return "neutral"
    except Exception:
        return "neutral"
