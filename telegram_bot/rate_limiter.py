from datetime import time
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Any

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int, key_prefix: str = "rate_limit_"):
        super().__init__()
        self.rate_limit = limit
        self.prefix = key_prefix
        self.last_called = {}

    async def on_pre_process_update(self, update: Update, data: Dict[str, Any]):
        if update.message:
            user_id = update.message.from_user.id
            key = f"{self.prefix}{user_id}"

            current_time = time()
            last_called = self.last_called.get(key)

            if last_called and current_time - last_called < self.rate_limit:
                await update.message.answer("Too many requests! Please wait before trying again.")
                return False  # This stops further processing of the update

            self.last_called[key] = current_time

    async def __call__(self, handler: Callable, event: Update, *args, **kwargs):
        # Ensure event is of type Update
        if isinstance(event, Update):
            await self.on_pre_process_update(event, kwargs)
        return await handler(event, *args, **kwargs)