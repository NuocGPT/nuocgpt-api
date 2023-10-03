from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_paginate import add_pagination

from api.auth.jwt_bearer import JWTBearer
from api.database import initiate_database
from ai.core.aws_service import AWSService

from api.routes.conversation import router as ConversationRouter
from api.routes.feedback import router as FeedbackRouter
from api.routes.auth import router as AuthRouter
from api.routes.me import router as MeRouter
from api.routes.admin import router as AdminRouter
from ai.routes.retrieval_system import router as DataIngestorRouter

app = FastAPI(
    title="NướcGPT API Documentation",
    version="1.0.0"
)

token_listener = JWTBearer()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start_database():
    await initiate_database()


s3_client = AWSService()
s3_client.download_from_s3()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to NướcGPT."}

app.include_router(AuthRouter, tags=["Auth"], prefix="/v1/auth")
app.include_router(
    ConversationRouter,
    tags=["Conversation"], 
    prefix="/v1/conversations",
    dependencies=[Depends(token_listener)]
)
app.include_router(
    FeedbackRouter,
    tags=["Feedback"],
    prefix="/v1/feedbacks",
    dependencies=[Depends(token_listener)]
)
app.include_router(
    MeRouter,
    tags=["Me"],
    prefix="/v1/me",
    dependencies=[Depends(token_listener)]
)
app.include_router(
    AdminRouter,
    tags=["Admin"],
    prefix="/v1/admin",
    dependencies=[Depends(token_listener)]
)
app.include_router(
    DataIngestorRouter,
    tags=["Data Ingestor"],
    prefix="/v1/ingest",
    dependencies=[Depends(token_listener)]
)

add_pagination(app)
