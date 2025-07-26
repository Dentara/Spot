# ai/whale_detector.py

import random

def get_whale_alerts(token: str = "TON") -> bool:
    """
    Simulyasiya üçün whale aktivliyi: Random olaraq 20% ehtimalla whale aktivliyi qaytarır.
    Gələcəkdə real API inteqrasiyası olacaq.
    """
    return random.random() < 0.2  # 20% ehtimal
