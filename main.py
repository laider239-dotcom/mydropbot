# main.py
import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Настройка логирования — чтобы видеть ошибки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Настройки бота ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен в переменных окружения!")
else:
    logger.info("✅ BOT_TOKEN загружен")

PORT = int(os.environ.get("PORT", 10000))

# === Бот и диспетчер ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Категории ===
categories_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Телефоны и аксессуары")],
        [KeyboardButton(text="🎧 Наушники и аудио")],
        [KeyboardButton(text="💻 Компьютеры и ноутбуки")],
        [KeyboardButton(text="🎮 Игры и приставки")],
        [KeyboardButton(text="🏠 Дом и сад")],
        [KeyboardButton(text="👗 Одежда и обувь")],
        [KeyboardButton(text="💄 Красота и здоровье")],
        [KeyboardButton(text="🐾 Товары для животных")],
        [KeyboardButton(text="🚗 Авто и мото")],
        [KeyboardButton(text="🧸 Детские товары")]
    ],
    resize_keyboard=True
)

# === Генерация описания через DeepSeek (БЕЗ отдельного файла) ===
def generate_description(product_name, category):
    """
    Генерация описания напрямую в main.py — чтобы НЕ БЫЛО проблем с импортом ai.py
    """
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        logger.error("❌ DEEPSEEK_API_KEY не установлен")
        return "Ошибка: ИИ не настроен. Ключ API не найден."

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"Напиши краткое, цепляющее описание для товара '{product_name}' в категории '{category}'. Сделай акцент на выгоде, удобстве, тренде. Не более 2–3 предложений. На русском языке."

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.8
    }

    try:
        logger.info("📡 Отправляю запрос в DeepSeek...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            logger.info("✅ Ответ от DeepSeek получен")
            return text
        else:
            logger.error(f"❌ Ошибка DeepSeek: {response.status_code} - {response.text}")
            return f"❌ Ошибка ИИ: {response.status_code}. Попробуй позже."
            
    except requests.exceptions.Timeout:
        logger.error("❌ Запрос к DeepSeek превысил время ожидания")
        return "❌ ИИ не ответил вовремя. Попробуй позже."
    except requests.exceptions.ConnectionError:
        logger.error("❌ Ошибка подключения к DeepSeek")
        return "❌ Не удалось подключиться к ИИ. Проверь интернет."
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка: {e}")
        return "❌ ИИ временно недоступен."

# === Обработчики бота ===
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🚀 Добро пожаловать в *DropHub*!\n"
        "Платформа для дропшиппинга в РФ.\n\n"
        "Что хочешь продавать?",
        reply_markup=categories_kb,
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text in [
    "📱 Телефоны и аксессуары", "🎧 Наушники и аудио", "💻 Компьютеры и ноутбуки",
    "🎮 Игры и приставки", "🏠 Дом и сад", "👗 Одежда и обувь",
    "💄 Красота и здоровье", "🐾 Товары для животных",
    "🚗 Авто и мото", "🧸 Детские товары"
])
async def category_chosen(message: types.Message):
    category = message.text
    product_name = category.replace("📱 ", "").replace("🎧 ", "").replace("💻 ", "").replace("🎮 ", "") \
                          .replace("🏠 ", "").replace("👗 ", "").replace("💄 ", "").replace("🐾 ", "") \
                          .replace("🚗 ", "").replace("🧸 ", "") + " по акции"

    await message.answer(
        f"🔍 Ищу трендовые товары в категории: *{category}*...",
        parse_mode="Markdown"
    )

    # Генерируем описание
    description = generate_description(product_name, category)

    # Показываем результат
    await message.answer(
        f"📦 *{product_name}*\n\n"
        f"💡 {description}\n\n"
        f"💰 Закупка: ~500 ₽\n"
        f"🎯 Продажа: 1490 ₽\n"
        f"🚚 Доставка: 10–14 дней",
        parse_mode="Markdown"
    )

# === Веб-сервер для Render ===
async def health_check(request):
    return web.Response(text="Bot is running", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

# === Запуск бота ===
async def main():
    # Запускаем веб-сервер
    await start_web_server()
    logger.info(f"✅ Веб-сервер запущен на порту {PORT}")

    # Запускаем бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
