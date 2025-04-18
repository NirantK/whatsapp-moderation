FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the WhatsApp analyzer from parent directory
COPY ../whatsapp_analyzer.py .

# Copy the web application
COPY . .

# Create a directory for temporary files
RUN mkdir -p /app/temp && chmod 777 /app/temp

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"] 