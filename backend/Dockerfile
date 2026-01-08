# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Копируем код проекта
COPY . /app/

# Устанавливаем netcat для проверки подключения к БД
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для запуска приложения
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

USER appuser

# Открываем порт
EXPOSE 8000

# Команда по умолчанию
CMD ["sh", "/app/entrypoint.sh"]
