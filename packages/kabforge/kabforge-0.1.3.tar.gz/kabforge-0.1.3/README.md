# Kabforge

Kabforge — это лёгкий и удобный фреймворк для создания Telegram-ботов на Python.  
Он создан с целью упростить работу с Telegram Bot API и сделать код максимально чистым и читаемым.

## Установка

```bash
pip install kabforge
```

## Быстрый старт

Пример простого бота:

```python
import asyncio
import logging
import os

from kabforge.client import Bot
from kabforge.dispatcher import Dispatcher
from kabforge.types import Message

logging.basicConfig(level=logging.INFO)

# Токен рекомендуется хранить в переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.on_message(command="/start")
async def start_handler(message: Message):
    await bot.send_message(chat_id=message.chat_id, text="Hello!")
    await message.test()


@dp.on_message(command="t")
async def t_handler(message: Message):
    await bot.send_message(chat_id=message.chat_id, text="Text message detected!")


@dp.on_sticker()
async def sticker_handler(message: Message):
    await bot.send_message(chat_id=message.chat_id, text="Sticker detected!")


@dp.on_message(command="huy")
async def huy_handler(message: Message):
    await message.answer(text="blya")


async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот экстренно выключен")
```

## Возможности

- Простая регистрация хендлеров через декораторы
- Поддержка различных типов апдейтов (сообщения, стикеры и др.)
- Удобная работа с объектами Telegram API
- Асинхронность (asyncio)

## Лицензия

MIT License
