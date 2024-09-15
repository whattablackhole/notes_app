from fastapi import FastAPI
from database import init_db
from app.controllers import router

async def lifespan(app: FastAPI):
    await init_db()
    
    yield
    
app = FastAPI(lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)