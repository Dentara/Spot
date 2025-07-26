# ai/gpt_rich_prompt.py

import openai
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt_rich(message: str) -> dict:
    """
    GPT-dən yalnız qərar yox, eyni zamanda səbəb və ehtimal istəyir.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "Sən peşəkar ticarət analizçisisən. Texniki göstəricilərə əsaslanaraq qərar verirsən "
                    "(BUY, SELL, NO_ACTION) və cavabı əsaslandırırsan. Riskləri, keçmiş nümunələri və ehtimalı da yaz."
                )},
                {"role": "user", "content": message}
            ]
        )
        content = response['choices'][0]['message']['content']
        lines = content.splitlines()
        decision = "NO_ACTION"
        for line in lines:
            if "BUY" in line.upper():
                decision = "BUY"
                break
            if "SELL" in line.upper():
                decision = "SELL"
                break
        return {
            "decision": decision,
            "explanation": content.strip()
        }
    except Exception as e:
        return {
            "decision": "NO_ACTION",
            "explanation": f"[Xəta]: {str(e)}"
        }
