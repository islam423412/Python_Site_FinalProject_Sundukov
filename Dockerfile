FROM python:3.12-slim

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app/

HEALTHCHECK --interval=3s --timeout=2s --retries=10 \
    CMD pg_isready -h db || exit 1
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000