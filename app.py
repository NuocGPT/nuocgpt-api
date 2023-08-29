from fastapi import FastAPI, Depends
from fastapi_paginate import add_pagination

from api.auth.jwt_bearer import JWTBearer
from config.config import initiate_database

from api.routes.conversation import router as ConversationRouter

app = FastAPI(
    title="NướcGPT API Documentation",
    version="1.0.0"
)

token_listener = JWTBearer()


@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to NướcGPT."}

app.include_router(ConversationRouter, tags=["Conversation"], prefix="/v1/conversations")

add_pagination(app)
