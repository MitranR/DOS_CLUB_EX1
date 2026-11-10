FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, entrypoint, and frontend source code
COPY main.py .
COPY backend ./backend
COPY frontend ./frontend

# Create data directory for persistent SQLite storage
RUN mkdir -p /app/data

# Expose FastAPI application port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

