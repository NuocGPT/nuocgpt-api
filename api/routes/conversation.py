from fastapi import APIRouter, Body, Depends
from fastapi_paginate import Page, paginate
from uuid import UUID
from typing import Annotated

from api.services.conversation import *
from api.models.conversation import Conversation
from api.models.message import Message
from api.schemas.conversation import *
from api.auth.jwt_handler import get_user_id


router = APIRouter()


@router.get("", response_model=Page[Conversation])
async def get_conversations(user_id: Annotated[dict, Depends(get_user_id)]):
    conversations = await retrieve_conversations(user_id)
    return paginate(conversations)


@router.post("", response_model=Message)
async def add_conversation_data(user_id: Annotated[dict, Depends(get_user_id)], data: AddConversationDto = Body(...)):
    return await add_conversation(user_id, data)


@router.put("/{id}", response_model=Union[bool, Conversation])
async def update_conversation(id: UUID, req: UpdateConversationDto = Body(...)):
    return await update_conversation_data(id, req.dict())


@router.get("/{id}/messages", response_model=Page[Message])
async def get_messages(id: UUID):
    messages = await retrieve_messages(id)
    return paginate(messages)


@router.post("/{id}/messages", response_model=Message)
async def add_message_data(user_id: Annotated[dict, Depends(get_user_id)], id: UUID, data: AddMessageDto = Body(...)):
    return await add_message(id, user_id, data)


@router.get("/{id}/generate-title", response_model=Union[bool, Conversation])
async def get_title(id: UUID):
    return await summarize_question(id)
