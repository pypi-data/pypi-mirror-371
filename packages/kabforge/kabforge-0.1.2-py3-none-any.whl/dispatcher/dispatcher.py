import httpx
import asyncio
import re
from typing import Callable, Dict, Any, List, Awaitable, Optional

from ..client import Bot
from ..types import Message


class Dispatcher:
    def __init__(self):
        # хендлеры по категориям
        self.handlers: Dict[str, List] = {
            "text": [],
            "sticker": [],
            "photo": [],
            "any": [],
            "command": [],
            "regex": [],
            "callback_query": []
        }
        self.middlewares: List[Callable[[Message], Awaitable]] = []

    async def run_middlewares(self, message: Message):
        for middleware in self.middlewares:
            await middleware(message)

    def use(self, middleware: Callable[[Message], Awaitable]):
        """Регистрация middleware"""
        self.middlewares.append(middleware)
        return middleware
    
    async def process_update(self, update: Dict[str, Any], bot: Bot):
        if "message" not in update:
            return

        message = Message(update["message"], bot=bot)
        tasks = []

        # запускаем middleware
        await self.run_middlewares(message)

        # 1) команды (/start, /help)
        if message.is_text and message.text.startswith("/"):
            for handler, command in self.handlers["command"]:
                if message.text.split()[0] == command:
                    tasks.append(handler(message))

        # 2) regex обработчики
        if message.is_text:
            for handler, pattern in self.handlers["regex"]:
                if re.match(pattern, message.text):
                    tasks.append(handler(message))

        # 3) обычные текстовые
        if message.is_text:
            for handler, cmd in self.handlers["text"]:
                if cmd is None or message.text.startswith(cmd):
                    tasks.append(handler(message))

        # 4) стикеры
        if message.is_sticker:
            for handler in self.handlers["sticker"]:
                tasks.append(handler(message))

        # 5) фото
        if message._data.get("photo"):
            for handler in self.handlers["photo"]:
                tasks.append(handler(message))

        # 6) универсальные (any)
        for handler in self.handlers["any"]:
            tasks.append(handler(message))

        if tasks:
            await asyncio.gather(*tasks)

    async def start_polling(self, bot: Bot, offset: Optional[int] = None, timeout: int = 10):
        current_offset = offset
        while True:
            try:
                updates = await bot.get_updates(offset=current_offset, timeout=timeout)
            except httpx.ReadTimeout:
                continue
            except Exception as e:
                print(f"[Polling error] {e}")
                await asyncio.sleep(1)
                continue

            for update in updates:
                await self.process_update(update=update, bot=bot)
                current_offset = update["update_id"] + 1

    def on_message(self, command: Optional[str] = None):
        def decorator(func: Callable[[Message], Awaitable]):
            self.handlers["text"].append((func, command))
            return func
        return decorator

    def on_command(self, command: str):
        def decorator(func: Callable[[Message], Awaitable]):
            self.handlers["command"].append((func, command))
            return func
        return decorator

    def on_regex(self, pattern: str):
        def decorator(func: Callable[[Message], Awaitable]):
            self.handlers["regex"].append((func, pattern))
            return func
        return decorator

    def on_sticker(self):
        def decorator(func: Callable[[Message], Awaitable]):
            self.handlers["sticker"].append(func)
            return func
        return decorator

    def on_photo(self):
        def decorator(func: Callable[[Message], Awaitable]):
            self.handlers["photo"].append(func)
            return func
        return decorator

    def on_any(self):
        def decorator(func: Callable[[Message], Awaitable]):
            self.handlers["any"].append(func)
            return func
        return decorator

    def on_callback_query(self):
        def decorator(func: Callable[[Dict[str, Any]], Awaitable]):
            self.handlers["callback_query"].append(func)
            return func
        return decorator
