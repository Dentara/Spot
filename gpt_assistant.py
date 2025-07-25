import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən ixtisaslaşmış maliyyə mütəxəssisisən. Ticarət qərarlarında yalnız texniki və analitik əsaslarla cavab ver. Fundamental şərh vermə. Yalnız cavab ver: BUY, SELL və ya NO_ACTION."},
                {"role": "user", "content": message}
            ]
        )
        return response['choices'][0]['message']['content'].strip().upper()
    except Exception as e:
        return "NO_ACTION"
