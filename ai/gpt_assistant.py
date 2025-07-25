import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən maliyyə üzrə ixtisaslaşmış ticarət analizçisisən. Yalnız texniki indikatorlara, candle-lara, trend ve xeberlere əsaslanıb qərar ver. Cavabın yalnız BUY, SELL və ya NO_ACTION olmalıdır."},
                {"role": "user", "content": message}
            ]
        )
        return response['choices'][0]['message']['content'].strip().upper()
    except Exception as e:
        return f"[Xəta baş verdi]: {str(e)}"
