# main.py
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv(8291090153:AAEWtyax6oMuRExHhgLpJ9TVl9dIqnpo2Vs)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

    await message.answer(
        "🔋 Умная розетка с Wi-Fi\n"
        "💰 Закупка: ~500 ₽\n"
        "🎯 Продажа: 1490 ₽\n"
        "🚚 Доставка: 10–14 дней\n\n"
        "Добавить этот товар в твой лендинг?",
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
