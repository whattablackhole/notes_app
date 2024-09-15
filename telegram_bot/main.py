import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
import dotenv
from aiogram.types import Message
from handlers.authorization import register_auth_handlers
from handlers.notes import register_note_handlers
from aiogram.filters import Command
from aiogram.fsm.middleware import FSMContextMiddleware
from aiogram.fsm.storage.memory import DisabledEventIsolation, MemoryStorage
from rate_limiter import RateLimitMiddleware



dotenv.load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(storage=storage)
dp.message.middleware(FSMContextMiddleware(storage=storage, events_isolation=DisabledEventIsolation()))
rate_limit_middleware = RateLimitMiddleware(limit=2)  # Limit to 2 seconds between messages

# 20 messages per minute per user
dp.message.middleware(rate_limit_middleware)  

# Global token storage
user_tokens = {}


async def setup_handlers(session):
    await register_auth_handlers(dp, user_tokens)
    await register_note_handlers(dp, session, user_tokens)

@dp.message(Command("start"))
async def start(message: Message):
    await message.reply("Welcome! Please log in by sending your username and password in the format: \n`/login username password`", parse_mode="Markdown")

@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "Here are the commands you can use:\n\n"
        "/login <username> <password> - Log in with your username and password.\n"
        "/notes [limit] [skip] - Get a list of your notes. Optional parameters: limit and skip.\n"
        "/search_by_tags - Search list of notes by related tags\n"
        "/create_note - Start the process of creating a new note.\n"
        "/help - Show this help message.\n"
    )
    await message.reply(help_text)


async def main():
    print("Running telegram bot...")

    async with aiohttp.ClientSession() as session:
        await setup_handlers(session)
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())