# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Render использует порт 10000 по умолчанию
PORT = int(os.environ.get("PORT", 10000))

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище
user_data = {}

# Клавиатура с категориями
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

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Я — DropBot 🤖\n"
        "Помогу запустить дропшиппинг за 5 минут.\n\n"
        "Что хочешь продавать?",
        reply_markup=categories_kb
    )

@dp.message(lambda m: m.text in [
    "📱 Телефоны и аксессуары", "🎧 Наушники и аудио", "💻 Компьютеры и ноутбуки",
    "🎮 Игры и приставки", "🏠 Дом и сад", "👗 Одежда и обувь",
    "💄 Красота и здоровье", "🐾 Товары для животных",
    "🚗 Авто и мото", "🧸 Детские товары"
])
async def category_chosen(message: types.Message):
    user_id = message.from_user.id
    category = message.text
    user_data[user_id] = {"category": category}

    await message.answer(
        f"🔍 Ищу трендовые товары в категории: *{category}*...",
        parse_mode="Markdown"
    )

    product_name = category.replace("📱 ", "").replace("🎧 ", "").replace("💻 ", "") + " по акции"
    await message.answer(
        f"📦 *{product_name}*\n\n"
        f"💡 Популярный товар с высокой наценкой. В тренде на TikTok.\n\n"
        f"💰 Закупка: ~600 ₽\n"
        f"🎯 Продажа: 1990 ₽\n"
        f"🚚 Доставка: 10–18 дней\n\n"
        f"Добавить в лендинг?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Да", callback_data="add_product"),
                    InlineKeyboardButton(text="❌ Нет", callback_data="next_product")
                ]
            ]
        )
    )

@dp.message(lambda message: message.text.startswith("/find"))
async def find_product(message: types.Message):
    query = message.text.replace("/find", "").strip()
    
    if not query:
        await message.answer("Напиши, что ищешь. Например: `/find наушники`", parse_mode="Markdown")
        return

    await message.answer(
        f"🔍 Ищу трендовые товары по запросу: *{query}*...",
        parse_mode="Markdown"
    )

    products = [
        {
            "name": f"Трендовые {query} 2025",
            "cost": "500 ₽",
            "price": "1790 ₽",
            "delivery": "12–16 дней",
            "desc": "Вирусный товар на TikTok. Высокая конверсия."
        },
        {
            "name": f"Премиум {query} с гарантией",
            "cost": "700 ₽",
            "price": "2290 ₽",
            "delivery": "10–14 дней",
            "desc": "Качественный товар с быстрой доставкой."
        }
    ]

    for p in products:
        await message.answer(
            f"✨ *{p['name']}*\n\n"
            f"💡 {p['desc']}\n\n"
            f"💰 Закупка: {p['cost']}\n"
            f"🎯 Продажа: {p['price']}\n"
            f"🚚 Доставка: {p['delivery']}\n\n"
            f"Добавить в лендинг?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Да",
                            callback_data=f"add_{p['name'][:10]}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Нет",
                            callback_data="next_product"
                        )
                    ]
                ]
            )
        )

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_product(callback: types.CallbackQuery):
    await callback.message.answer(
        "✅ Отлично! Товар добавлен.\n\n"
        "Скоро я создам для тебя лендинг в Notion — просто подожди!"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "next_product")
async def next_product(callback: types.CallbackQuery):
    await callback.message.answer("🔍 Ищу другой товар…")
    await callback.answer()

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

# === Запуск бота и сервера ===
async def main():
    # Запускаем веб-сервер
    await start_web_server()
    print(f"Web server started on port {PORT}")

    # Запускаем бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка бота: {e}")
        # Не перезапускаем — пусть Render сам перезапустит сервис

if __name__ == "__main__":
    asyncio.run(main())
