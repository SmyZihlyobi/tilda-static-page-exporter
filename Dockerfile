# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Установка git и сетевых утилит
RUN apt-get update && \
    apt-get install -y \
    git \
    iputils-ping \
    dnsutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Настройка Git
RUN git config --system user.name "Tilda Exporter" && \
    git config --system user.email "tilda-exporter@example.com" && \
    git config --system core.autocrlf false && \
    git config --system safe.directory '*'

# Настройка DNS
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Set the working directory to /app
WORKDIR /app

# Copy only the necessary files into the container at /app
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary application files
COPY . .

# Create directory for static files and initialize git
RUN mkdir -p static && \
    cd static && \
    git init && \
    git config --local user.name "Tilda Exporter" && \
    git config --local user.email "tilda-exporter@example.com"

# Expose port 8000 for the Flask application
EXPOSE 8000

# Проверка сети перед запуском
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f https://static.tildacdn.com || exit 1

# Запуск приложения
CMD ["python", "main.py"]

