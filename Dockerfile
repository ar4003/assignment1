# Use a slim Python base image with version 3.11
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies required for many Python packages (e.g. numpy, pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip & install wheel before other packages
RUN pip install --upgrade pip wheel setuptools

# Install Python dependencies from requirements file without cache to avoid conflicts
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project code into container
COPY . .

# Expose the port your app listens on (adjust if needed)
EXPOSE 8000

# Run the main Python file named main.py (instead of app.py)
CMD ["python", "main.py"]
