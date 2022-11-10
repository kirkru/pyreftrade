# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# @app.get("/users")
# async def get_users():
#     return {"message": "Get Users!"}

from fastapi import FastAPI

from app.api.api_v1.api import router as api_router
from mangum import Mangum

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!"}


app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)