from aiogram.types import Message

async def get_user_token(message: Message, user_tokens: dict):
    return user_tokens.get(message.from_user.id)

# async def save_user_token(message: Message, token: str):
#     user_tokens[message.from_user.id] = token