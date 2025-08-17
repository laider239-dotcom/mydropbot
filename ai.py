# ai.py
import requests
import os

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def generate_description(product_name, category):
    if not DEEPSEEK_API_KEY:
        return "Популярный товар с высокой наценкой. В тренде."

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Напиши краткое, цепляющее описание для товара '{product_name}' в категории '{category}'.
    Сделай акцент на выгоде, удобстве, тренде.
    Не более 2–3 предложений.
    На русском языке.
    """

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.8
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ИИ временно недоступен. Товар: {product_name}"
