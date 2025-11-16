# Use Python 3.11
FROM python:3.11-slim

# Set working directory to /app/backend
WORKDIR /app/backend

# Copy only backend folder contents
COPY backend/ .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run from backend directory directly
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]