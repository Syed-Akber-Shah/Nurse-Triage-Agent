FROM python:3.11-slim

WORKDIR /app/backend

COPY backend/ .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Use Python script to start (handles PORT variable properly)
CMD ["python", "start.py"]