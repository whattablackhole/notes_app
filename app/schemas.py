from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    tags: Optional[List[TagBase]]

class NoteUpdate(NoteBase):
    tags: Optional[List[TagBase]]

class NoteInDB(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[TagBase]]

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str