# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Импортируем модули
try:
    from ai import generate_description
except ImportError:
    def generate_description(name, cat): return "Популярный товар с высокой наценкой."

try:
    from russian_suppliers import find_russian_product
except ImportError:
    def find_russian_product(query):
        return {
            "name": f"Трендовый {query}",
            "price_rub": 450,
            "image": "https://pics.aliexpress.com/...jpg",
            "delivery_days": 5,
            "supplier": "AliExpress (через РФ-склад)"
        }

try:
    from notion import create_landing_page
except ImportError:
    pass

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Бот и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Категории
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
        "🚀 Добро пожаловать в *DropHub*!\n"
        "Платформа для дропшиппинга в РФ.\n\n"
        "Что хочешь продавать?",
        reply_markup=categories_kb,
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text in ["Электроника", "Одежда", "Гаджеты", "Дом и дача", "Красота и уход"])
async def category_chosen(message: types.Message):
    query = message.text
    await message.answer("🔍 Ищу товары у российских поставщиков...")

    # Ищем товар
    product = find_russian_product(query)
    if not product:
        await message.answer("❌ Не удалось найти товар. Попробуй позже.")
        return

    # Расчёт
    cost = product["price_rub"]
    delivery_cost = 150  # Доставка до клиента
    sale_price = int(cost * 2.2)  # Наценка 120%
    profit = sale_price - cost - delivery_cost
    margin = int((profit / (cost + delivery_cost)) * 100)

    # Описание от ИИ
    description = generate_description(product["name"], query)

    # Показываем
    await message.answer_photo(
        photo=product["image"],
        caption=(
            f"📦 *{product['name']}*\n\n"
            f"💡 {description}\n\n"
            f"🛒 Поставщик: *{product['supplier']}*\n"
            f"🚚 Доставка: {product['delivery_days']} дней\n\n"
            f"💰 Закупка: {cost} ₽\n"
            f"🎯 Продажа: {sale_price} ₽\n"
            f"📈 Прибыль: {profit} ₽ ({margin}%)\n\n"
            f"Создать лендинг?"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Да", callback_data="create_landing"),
                    InlineKeyboardButton(text="❌ Нет", callback_data="next_product")
                ]
            ]
        )
    )

@dp.callback_query(lambda c: c.data == "create_landing")
async def create_landing(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Здесь можно сохранить выбранный товар для пользователя
    try:
        # Предположим, что у нас есть notion.py
        from notion import create_landing_page
        landing_url = create_landing_page({
            "name": "Умная розетка",
            "price": "1990 ₽",
            "description": "Управляется голосом через Алису"
        })
        await callback.message.answer(
            "✅ Лендинг создан!\n\n"
            f"👉 {landing_url}\n\n"
            "Копируй ссылку и публикуй в Telegram / TikTok!"
        )
    except:
        await callback.message.answer(
            "✅ Отлично! Товар добавлен.\n\n"
            "Скоро будет лендинг. Пока можешь сделать скриншот этого сообщения."
        )
    await callback.answer()

# === Веб-сервер для Render ===
async def health_check(request):
    return web.Response(text="DropHub is running", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

# === Запуск ===
async def main():
    await start_web_server()
    print(f"✅ Веб-сервер запущен на порту {PORT}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
