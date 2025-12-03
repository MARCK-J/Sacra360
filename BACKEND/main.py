from fastapi import FastAPI
from app.core.config import settings

# Minimal FastAPI app used by tests. Tests may override DB dependency at runtime.
app = FastAPI(title=settings.service_name)

@app.get('/api/v1/health')
async def health():
    return {"status": "ok"}
