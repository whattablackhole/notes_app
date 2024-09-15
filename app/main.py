from fastapi import FastAPI
from app.database import init_db
from app.controllers.notes import notes_router
from app.controllers.users import users_router

async def lifespan(app: FastAPI):
    await init_db()
    
    yield
    
app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(notes_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)