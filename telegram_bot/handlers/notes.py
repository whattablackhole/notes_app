from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import aiohttp
from state_machine import NoteForm, NoteSearch
from token_manager import get_user_token
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from config import API_BASE_URL



async def register_note_handlers(dp: Dispatcher, session, user_tokens: dict):
    @dp.message(Command("search_by_tags"))
    async def handle_search_notes_start(message: Message, state: FSMContext):
        await search_notes_start(message, state)

    @dp.message(StateFilter(NoteSearch.tags))
    async def handle_search_notes(message: Message, state: FSMContext):
        await process_search_tags(message, session, user_tokens, state)

    @dp.message(Command("notes"))
    async def handle_get_notes(message: Message):
        await get_notes(message, session, user_tokens)
    
    @dp.message(Command("create_note"))
    async def handle_create_note_start(message: Message, state: FSMContext):
        await create_note_start(message, state)

    @dp.message(StateFilter(NoteForm.title))
    async def handle_process_title(message: Message, state: FSMContext):
        await process_title(message, state)

    @dp.message(StateFilter(NoteForm.content))
    async def handle_process_content(message: Message, state: FSMContext):
        await process_content(message, state)

    @dp.message(StateFilter(NoteForm.tags))
    async def handle_process_tags(message: Message, state: FSMContext):
        await process_tags(message, state, user_tokens)




async def get_notes(message: Message, session: aiohttp.ClientSession, token_list: dict):
    token = await get_user_token(message, token_list)
    if not token:
        await message.reply("Please log in first.")
        return
    
    default_limit = 10
    default_skip = 0

    try:
        parts = message.text.split()
        limit = int(parts[1]) if len(parts) > 1 else default_limit
        skip = int(parts[2]) if len(parts) > 2 else default_skip
    except ValueError:
        await message.reply("Invalid format. Use: /notes <limit> <skip>")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": limit, "skip": skip}
    
    async with session.get(f"{API_BASE_URL}/notes/", headers=headers, params=params) as resp:
        if resp.status == 200:
            notes = await resp.json()
            if notes:
                notes_list = "\n".join([f"{note['title']}: {note['content']}" for note in notes])
                await message.reply(f"Your Notes:\n{notes_list}")
            else:
                await message.reply("No notes found.")
        else:
            await message.reply("Failed to retrieve notes.")

async def create_note_start(message: Message, state: FSMContext):
    await message.reply("Enter the note title:")
    await state.set_state(NoteForm.title)

async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.reply("Now enter the note content:")
    await state.set_state(NoteForm.content)

async def process_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.reply("Enter comma-separated tags for the note (or type 'skip' if you don't want to add tags):")
    await state.set_state(NoteForm.tags)

async def process_tags(message: Message, state: FSMContext, token_list: dict):
    tags = message.text.split(',') if message.text != 'skip' else []
    await state.update_data(tags=tags)

    data = await state.get_data()
    title = data['title']
    content = data['content']
    
    token = await get_user_token(message, token_list)  # Retrieve the user's token
    if not token:
        await message.reply("Please log in first.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    note_data = {
        "title": title,
        "content": content,
        "tags": [{"name": tag} for tag in tags]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}/notes/", json=note_data, headers=headers) as resp:
            if resp.status == 200:
                await message.reply("Note created successfully!")
            else:
                await message.reply("Failed to create note.")
    
    await state.clear()


async def search_notes_start(message: types.Message, state: FSMContext):
    await message.reply("Enter comma-separated tags to search for notes:")
    await state.set_state(NoteSearch.tags)


async def process_search_tags(message: types.Message, session: aiohttp.ClientSession, token_list, state: FSMContext):
    tags = message.text.split(',')
    formatted_tags = [{"name": tag.strip()} for tag in tags]

    token = await get_user_token(message, token_list)
    if not token:
        await message.reply("Please log in first.")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with session.post(f"{API_BASE_URL}/notes/search/", json=formatted_tags, headers=headers) as resp:
        if resp.status == 200:
            notes = await resp.json()
            notes_list = "\n".join([f"{note['title']}: {note['content']}" for note in notes])
            await message.reply(f"Found Notes:\n{notes_list}")
        else:
            await message.reply("No notes found with the given tags.")
    
    await state.clear()






