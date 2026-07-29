import os
import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

# ===== ТВОЙ ТОКЕН (ВСТАВЛЕН) =====
TOKEN = "8708501905:AAEVoFoEDuDs3rGxkDqs3tubdRLlA5mEXmQ"

# ===== НАСТРОЙКИ (МЕНЯЙ ЗДЕСЬ) =====
LENGTH = 5          # 5 или 6
MODE = 'letters'    # 'letters' / 'digits' / 'all'
COUNT = 10          # 1-50

# ===== КОД БОТА (НЕ ТРОГАЙ) =====
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

def generate_names(length, mode, count):
    chars = string.ascii_lowercase if mode == 'letters' else string.ascii_lowercase + string.digits if mode == 'digits' else string.ascii_lowercase + string.digits + "_"
    names = []
    attempts = 0
    while len(names) < count and attempts < count * 10:
        name = ''.join(random.choices(chars, k=length))
        if name[0] in string.digits or name[0] == '_' or name[-1] == '_' or '__' in name or name in names:
            attempts += 1
            continue
        names.append(name)
        attempts += 1
    return names

async def check_name(name):
    try:
        await bot.get_chat(f"@{name}")
        return False
    except TelegramBadRequest as e:
        if "chat not found" in str(e).lower() or "not occupied" in str(e).lower():
            return True
        return False
    except:
        return False

def check_liquidity(name):
    score = 0
    if len(name) == 5: score += 3
    elif len(name) == 6: score += 2
    if name.isalpha(): score += 3
    elif any(c.isdigit() for c in name): score += 1
    if len(set(name)) <= 3: score += 2
    if score >= 7: return "🔵 ВЫСОКАЯ"
    elif score >= 4: return "🟡 СРЕДНЯЯ"
    else: return "🔴 НИЗКАЯ"

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer("🤖 <b>Бот для поиска юзернеймов</b>\n\n/search — найти свободные username")

@dp.message(Command("search"))
async def search(m: Message):
    status = await m.answer("🔍 Ищу...")
    names = generate_names(LENGTH, MODE, COUNT)
    if not names:
        await status.edit_text("❌ Ошибка генерации")
        return
    results, free = [], 0
    for i, name in enumerate(names):
        if i % 3 == 0:
            await status.edit_text(f"🔍 Проверено: {i}/{len(names)}, найдено: {free}")
        available = await check_name(name)
        if available:
            free += 1
            results.append(f"✅ @{name} — СВОБОДЕН | {check_liquidity(name)}")
        else:
            results.append(f"❌ @{name} — ЗАНЯТ")
        await asyncio.sleep(1.5)
    await status.edit_text(f"🔍 <b>Результаты</b>\n✅ Свободных: {free}\n❌ Занятых: {len(names)-free}\n\n" + "\n".join(results[:20]))

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())