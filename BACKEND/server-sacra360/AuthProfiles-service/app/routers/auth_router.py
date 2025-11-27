from fastapi import APIRouter

router = APIRouter()


@router.get("/login")
async def login_stub():
    return {"message": "login placeholder"}
