
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV TELEGRAM_TOKEN=7542726745:AAFBMWGOHq3mISxp4x7iU0m3TxM2rpYZN-w

CMD ["python", "main.py"]