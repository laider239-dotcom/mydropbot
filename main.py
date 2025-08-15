# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Render может передавать PORT, но для бота это не обязательно
PORT = int(os.environ.get("PORT", 8000))

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище данных пользователей
user_data = {}

# Клавиатура с категориями
categories_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Электроника")],
        [KeyboardButton(text="Одежда")],
        [KeyboardButton(text="Гаджеты")],
        [KeyboardButton(text="Дом и дача")],
        [KeyboardButton(text="Красота и уход")]
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

@dp.message(lambda m: m.text in ["Электроника", "Одежда", "Гаджеты", "Дом и дача", "Красота и уход"])
async def category_chosen(message: types.Message):
    user_id = message.from_user.id
    category = message.text
    user_data[user_id] = {"category": category}

    await message.answer(
        f"🔍 Ищу трендовые товары в категории: *{category}*...",
        parse_mode="Markdown"
    )

    # Генерируем описание через ИИ (из ai.py)
    product_name = "Умная розетка с Wi-Fi"
    description = "Умная розетка, которую можно включать голосом через Алису. Управление техникой из любой точки дома."
    
    # Показываем товар
    await message.answer(
        f"🔋 {product_name}\n\n"
        f"💡 {description}\n\n"
        f"💰 Закупка: ~500 ₽\n"
        f"🎯 Продажа: 1490 ₽\n"
        f"🚚 Доставка: 10–14 дней\n\n"
        f"Добавить в лендинг?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Да", callback_data="add_product"),
                    InlineKeyboardButton(text="❌ Нет", callback_data="next_product")
                ]
            ]
        )
    )

@dp.callback_query(lambda c: c.data == "add_product")
async def add_product(callback: types.CallbackQuery):
    await callback.message.answer("✅ Товар добавлен! Скоро создам для тебя лендинг в Notion.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "next_product")
async def next_product(callback: types.CallbackQuery):
    await callback.message.answer("🔍 Ищу другой товар...")
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)  # Убрали resolve_allowed_updates()

if __name__ == "__main__":
    asyncio.run(main())

