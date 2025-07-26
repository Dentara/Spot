import requests
import time

TELEGRAM_TOKEN = "8044814129:AAGuUT5ORrNjEm26PzeSshLMsMxW2aymIf8"
CHAT_ID = "91607116"
last_msg_time = 0  # Rate-limit üçün

def send_telegram_message(text: str):
    global last_msg_time
    now = time.time()

    # Telegram mesaj limiti (saniyədə max 1 mesaj)
    if now - last_msg_time < 1.1:
        time.sleep(1.1)
    last_msg_time = now

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"⚠️ Telegram mesajı göndərilə bilmədi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Telegram xəta: {e}")