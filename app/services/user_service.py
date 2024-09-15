from fastapi import HTTPException, Request, Depends, status
from sqlalchemy import select

from app.models import User
from app.utils.jwt import decode_jwt_token
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


async def get_user_from_token(db: AsyncSession, token: str) -> User:
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    auth_string = auth_header.split(" ")

    if len(auth_string) < 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    
    token = auth_string[1]

    user = await get_user_from_token(db, token)
    
    return user