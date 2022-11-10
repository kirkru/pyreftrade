from urllib.request import Request
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "Users!"}

@router.get("/test")
async def get_users_test():
    return {"message": "test Users!"}

@router.get("/t2")
async def get_users_t2(request: Request):
    query_params = request.query_params
    print(query_params)
    print(type(query_params))
    return {"message": "Got query params"}