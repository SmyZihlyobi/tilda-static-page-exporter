FROM python:3.11-slim

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание базовой директории для работы приложения
RUN mkdir -p /app

WORKDIR /app

# Установка необходимых зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Запуск приложения
CMD ["python", "main.py"] 