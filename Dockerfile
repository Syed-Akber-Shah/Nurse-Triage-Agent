# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/ ./backend/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Expose port
EXPOSE 8000

# Change to backend directory and start server
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]