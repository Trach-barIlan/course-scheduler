# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Increase timeout for large packages and install torch/gliner first
RUN pip install --no-cache-dir --default-timeout=1000 torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application (will use uvicorn for FastAPI)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
