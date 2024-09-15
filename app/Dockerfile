FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


ENV ALEMBIC_DATABASE_URL=postgresql://postgres:admin@postgres/notes_db


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000


CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8005"]