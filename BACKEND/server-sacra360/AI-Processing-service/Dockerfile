FROM python:3.11-slim

WORKDIR /app

# Copy application code
COPY app /app

# Minimal runtime dependencies
RUN pip install --no-cache-dir fastapi uvicorn

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
