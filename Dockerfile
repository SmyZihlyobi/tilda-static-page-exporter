# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Установка git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy only the necessary files into the container at /app
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary application files
COPY . .

# Create directory for static files
RUN mkdir -p static

# Expose port 8000 for the Flask application
EXPOSE 8000

# Запуск через Python
CMD ["python", "main.py"]

