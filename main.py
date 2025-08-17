# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Render использует порт 10000 по умолчанию
PORT = int(os.environ.get("PORT", 10000))

# === Бот и диспетчер ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Временное хранилище ===
user_data = {}

# === Попробуем подключить ИИ ===
try:
    from ai import generate_description
except ImportError:
    # Если ai.py нет — используем заглушку
    def generate_description(product_name, category):
        return "Популярный товар с высокой наценкой. В тренде."

# === Клавиатура с категориями ===
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

# === Обработчик /start ===
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🚀 Добро пожаловать в *DropHub*!\n"
        "Платформа для дропшиппинга в РФ.\n\n"
        "Что хочешь продавать?",
        reply_markup=categories_kb,
        parse_mode="Markdown"
    )

# === Обработчик выбора категории ===
@dp.message(lambda m: m.text in [
    "📱 Телефоны и аксессуары", "🎧 Наушники и аудио", "💻 Компьютеры и ноутбуки",
    "🎮 Игры и приставки", "🏠 Дом и сад", "👗 Одежда и обувь",
    "💄 Красота и здоровье", "🐾 Товары для животных",
    "🚗 Авто и мото", "🧸 Детские товары"
])
async def category_chosen(message: types.Message):
    user_id = message.from_user.id
    category = message.text

    # Убираем эмодзи для чистого названия
    product_name = category.replace("📱 ", "").replace("🎧 ", "").replace("💻 ", "").replace("🎮 ", "") \
                          .replace("🏠 ", "").replace("👗 ", "").replace("💄 ", "").replace("🐾 ", "") \
                          .replace("🚗 ", "").replace("🧸 ", "") + " по акции"

    # Генерируем описание через ИИ
    description = generate_description(product_name, category)

    # Показываем, что ищем
    await message.answer(
        f"🔍 Ищу трендовые товары в категории: *{category}*...",
        parse_mode="Markdown"
    )

    # Показываем товар
    await message.answer(
        f"📦 *{product_name}*\n\n"
        f"💡 {description}\n\n"
        f"💰 Закупка: ~500 ₽\n"
        f"🎯 Продажа: 1490 ₽\n"
        f"🚚 Доставка: 10–14 дней\n\n"
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

# === Обработчик кнопок ===
@dp.callback_query(lambda c: c.data == "add_product")
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

# === Веб-сервер для Render (чтобы не было "No open ports detected") ===
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
    print(f"✅ Веб-сервер запущен на порту {PORT}")

    # Запускаем бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")

# === Запуск ===
if __name__ == "__main__":
    asyncio.run(main())
