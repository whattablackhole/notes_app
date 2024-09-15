from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import List
from app.models import NoteORM
from app.schemas import NoteCreate, NoteUpdate, NoteInDB
from database import get_db

router = APIRouter()

@router.post("/notes/", response_model=NoteInDB)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    new_note = NoteORM(
        title=note.title,
        content=note.content,
        tags=note.tags,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

@router.get("/notes/{note_id}", response_model=NoteInDB)
async def read_note(note_id: int, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(NoteORM).where(NoteORM.id == note_id))
    note = query.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.get("/notes/", response_model=List[NoteInDB])
async def read_notes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(NoteORM).offset(skip).limit(limit))
    notes = query.scalars().all()
    return notes

@router.put("/notes/{note_id}", response_model=NoteInDB)
async def update_note(note_id: int, updated_note: NoteUpdate, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(NoteORM).where(NoteORM.id == note_id))
    note = query.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = updated_note.title
    note.content = updated_note.content
    note.tags = updated_note.tags
    note.updated_at = datetime.now()

    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/notes/{note_id}", response_model=NoteInDB)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(NoteORM).where(NoteORM.id == note_id))
    note = query.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await db.delete(note)
    await db.commit()
    return note