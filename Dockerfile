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
ARG GIT_CONFIG_NAME="Tilda Exporter"
ARG GIT_CONFIG_EMAIL="tilda-exporter@example.com"

RUN git config --system user.name "${GIT_CONFIG_NAME}" && \
    git config --system user.email "${GIT_CONFIG_EMAIL}" && \
    git config --system core.autocrlf false && \
    git config --system safe.directory '*'

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
    git config --local user.name "${GIT_CONFIG_NAME}" && \
    git config --local user.email "${GIT_CONFIG_EMAIL}"

# Expose port 8000 for the Flask application
EXPOSE 8000

# Проверка сети перед запуском
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f https://static.tildacdn.com || exit 1

# Запуск приложения
CMD ["python", "main.py"]

