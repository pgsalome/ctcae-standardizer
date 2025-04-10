FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/notebooks

# Copy source code
COPY . .

# Set environment variable for IRIS
ENV IRISINSTALLDIR="/usr"

# Expose ports
EXPOSE 8000

# Install the package in development mode
RUN pip install -e .

# Default command
CMD ["python", "-c", "import time; print('Container is running...'); time.sleep(infinity)"]