from fastapi import FastAPI, Depends

from api.auth.jwt_bearer import JWTBearer
from api.config.config import initiate_database

app = FastAPI()

token_listener = JWTBearer()


@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to NướcGPT."}
