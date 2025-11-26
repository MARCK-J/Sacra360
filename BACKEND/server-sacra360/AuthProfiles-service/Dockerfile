FROM python:3.11-slim

WORKDIR /app

# Copy the package as /app/app so imports like `app.routers` resolve
COPY app /app/app

RUN pip install --no-cache-dir fastapi uvicorn

EXPOSE 8001

# Run the ASGI app via the package path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
