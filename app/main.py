from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database import init_db
from app.controllers.notes import notes_router
from app.controllers.users import users_router
from fastapi import FastAPI, Request, HTTPException
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging
from logging.handlers import TimedRotatingFileHandler
from app.limiter import limiter

async def lifespan(app: FastAPI):
    await init_db()
    
    yield
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(SlowAPIMiddleware)

app.state.limiter = limiter

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(notes_router)


# Configure logging
def setup_logging():
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    # Create a file handler that logs to a file with daily rotation
    handler = TimedRotatingFileHandler("/app/app.log", when="midnight", interval=1)
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

logger = setup_logging()


from fastapi import HTTPException

# Global error handling for general exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# Handle HTTP exceptions (e.g., 404, 400)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Handle rate limiting errors
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded: {exc}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)