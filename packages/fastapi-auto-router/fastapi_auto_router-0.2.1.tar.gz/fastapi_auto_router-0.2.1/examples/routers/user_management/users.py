from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def list_users():
    return {"message": "List users"} 