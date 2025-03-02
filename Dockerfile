FROM python:3.11-slim

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