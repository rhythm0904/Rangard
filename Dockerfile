FROM python:3.11-slim

# System dependencies needed by some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create quarantine directory
RUN mkdir -p /tmp/ransomguard_quarantine

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
