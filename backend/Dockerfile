# Use the official Python slim image
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn users.wsgi:application --bind 0.0.0.0:8000"]
