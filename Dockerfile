FROM python:3.11-slim

WORKDIR /app/backend

COPY backend/ .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Use Python script to start (handles PORT variable properly)
# CMD ["python", "start.py"]

# Use fixed port 8000 - Railway will map it automatically
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["uvicorn", "main:app", "--port", "8000"]