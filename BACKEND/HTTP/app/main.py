from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"service": "api-gateway-placeholder", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
