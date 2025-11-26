from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"service": "files-service", "status": "placeholder"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
