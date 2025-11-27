from fastapi import APIRouter

router = APIRouter()


@router.get("/profiles")
async def profiles_stub():
    return {"profiles": []}
