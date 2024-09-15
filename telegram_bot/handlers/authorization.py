from aiogram import Router
from aiogram.types import Message
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import API_BASE_URL

async def login(message: Message, user_tokens: dict):
    try:
        _, username, password = message.text.split()
    except ValueError:
        await message.reply("Invalid login format. Use: /login username password")
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}/users/token/", json={"username": username, "password": password}) as resp:
            if resp.status == 200:
                user_tokens[message.from_user.id] = (await resp.json())['access_token']
                await message.reply("Logged in successfully! Here are the available commands:\n"
                                    "/notes - Get a list of your notes\n"
                                    "/create_note - Start creating a new note\n"
                                    "/help - List available commands")
            else:
                await message.reply("Login failed! Please check your credentials.")


async def register_auth_handlers(dp: Dispatcher, user_tokens: dict):
    @dp.message(Command("login"))
    async def handle_get_notes(message: Message):
        await login(message, user_tokens)