import requests

TELEGRAM_TOKEN = "8044814129:AAGuUT5ORrNjEm26PzeSshLMsMxW2aymIf8"
CHAT_ID = "91607116"


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"⚠️ Telegram mesajı göndərilə bilmədi: {response.text}")
    except Exception as e:
        print(f"❌ Telegram xəta: {e}")
