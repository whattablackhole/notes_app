from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List
from app.models import NoteORM, Tag, User
from app.schemas import NoteCreate, NoteUpdate, NoteInDB, TagBase
from app.services.user_service import get_current_user
from database import get_db

notes_router = APIRouter()
@notes_router.post("/notes/", response_model=NoteInDB)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_note = NoteORM(
        title=note.title,
        content=note.content,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id=current_user.id
    )
    
    if note.tags:
        tag_objects = []
        for tag in note.tags:
            result = await db.execute(select(Tag).filter_by(name=tag.name))
            existing_tag = result.scalars().first()
            
            if existing_tag:
                tag_objects.append(existing_tag)
            else:
                new_tag = Tag(name=tag.name)
                db.add(new_tag)
                await db.commit()
                tag_objects.append(new_tag)

        new_note.tags = tag_objects

    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    
    return new_note

@notes_router.get("/notes/{note_id}", response_model=NoteInDB)
async def read_note(note_id: int, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(NoteORM).options(selectinload(NoteORM.tags)).where(NoteORM.id == note_id))
    note = query.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@notes_router.get("/notes/", response_model=List[NoteInDB])
async def read_notes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(NoteORM).options(selectinload(NoteORM.tags)).offset(skip).limit(limit)
    )
    notes = query.scalars().all()
    return notes

@notes_router.put("/notes/{note_id}", response_model=NoteInDB)
async def update_note(note_id: int, updated_note: NoteUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = await db.execute(
        select(NoteORM).options(selectinload(NoteORM.tags)).where(NoteORM.id == note_id)
    )
    note = query.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")

    note.title = updated_note.title
    note.content = updated_note.content
    note.updated_at = datetime.now()

    if updated_note.tags is not None:
        note.tags = []
        
        tag_objects = []
        for tag in updated_note.tags:
            result = await db.execute(select(Tag).filter_by(name=tag.name))
            existing_tag = result.scalars().first()
            
            if existing_tag:
                tag_objects.append(existing_tag)
            else:
                new_tag = Tag(name=tag.name)
                db.add(new_tag)
                await db.commit()
                tag_objects.append(new_tag)
        
        note.tags = tag_objects

    await db.commit()
    await db.refresh(note)
    return note

@notes_router.delete("/notes/{note_id}", response_model=NoteInDB)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = await db.execute(
        select(NoteORM).options(selectinload(NoteORM.tags)).where(NoteORM.id == note_id)
    )
    note = query.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    
    await db.delete(note)
    await db.commit()
    return note

@notes_router.get("/notes/search/", response_model=List[NoteInDB])
async def search_notes_by_tags(tags: List[TagBase], db: AsyncSession = Depends(get_db)):
    if not tags:
        raise HTTPException(status_code=400, detail="At least one tag must be provided")

    tag_names = [tag.name for tag in tags]

    tag_results = await db.execute(select(Tag).filter(Tag.name.in_(tag_names)))
    matched_tags = tag_results.scalars().all()

    if not matched_tags:
        raise HTTPException(status_code=404, detail="No tags found")

    query = await db.execute(
        select(NoteORM).options(selectinload(NoteORM.tags))
        .join(NoteORM.tags)
        .filter(Tag.name.in_(tag_names))
        .distinct()
    )
    notes = query.scalars().all()

    if not notes:
        raise HTTPException(status_code=404, detail="No notes found for the provided tags")

    return notes

