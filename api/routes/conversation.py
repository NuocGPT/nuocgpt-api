from fastapi import APIRouter, Body
from fastapi_paginate import Page, paginate
from uuid import UUID

from api.services.conversation import *
from api.models.conversation import Conversation
from api.models.message import Message
from api.schemas.conversation import *


router = APIRouter()


@router.get("", response_description="Conversations retrieved", response_model=Page[Conversation])
async def get_conversations():
    conversations = await retrieve_conversations()
    return paginate(conversations)


@router.post(
    "",
    response_description="Conversation data added into the database",
    response_model=Conversation,
)
async def add_conversation_data(data: AddConversationDto = Body(...)):
    return await add_conversation(data)


@router.get(
    "/{id}/messages",
    response_description="Get Message to Conversation",
    response_model=Page[Message],
)
async def get_messages(id: UUID):
    messages = await retrieve_messages(id)
    return paginate(messages)


@router.post(
    "/{id}/messages",
    response_description="Add Message to Conversation",
    response_model=Message,
)
async def add_message_data(id: UUID, data: AddMessageDto = Body(...)):
    return await add_message(id, data)
