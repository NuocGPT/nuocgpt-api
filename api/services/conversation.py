from typing import List, Union
from uuid import UUID
from datetime import datetime

from api.models.conversation import Conversation
from api.models.message import Message, AuthorTypeEnum, ContentTypeEnum
from api.schemas.conversation import *
from ai.routes.chat import chat
from ai.schemas.schemas import QARequest


async def retrieve_conversations() -> List[Conversation]:
    conversations = await Conversation.all().sort("-updated_at").to_list()
    return conversations


async def add_conversation(data: AddConversationDto) -> Message:
    new_conversation = Conversation(title=data.title, author_id=data.author_id)
    conversation = await new_conversation.create()
    user_message = Message(
        conversation_id=conversation.id,
        author={"id": data.author_id, "role": AuthorTypeEnum.user},
        content={"content_type": ContentTypeEnum.text, "parts": [data.messages[0]["content"]]}
    )
    await user_message.create()
    answer = await chat(QARequest(messages=data.messages))
    system_message = Message(
        conversation_id=conversation.id,
        author={"role": AuthorTypeEnum.system},
        content={"content_type": ContentTypeEnum.text, "parts": [answer]}
    )
    return await system_message.create()


async def retrieve_messages(id) -> List[Message]:
    messages = await Message.find(Message.conversation_id == id).sort("-created_at").to_list()
    return messages


async def add_message(id: UUID, data: AddMessageDto) -> Message:
    user_message = Message(
        conversation_id=id,
        author={"id": data.author_id, "role": AuthorTypeEnum.user},
        content={"content_type": ContentTypeEnum.text, "parts": [data.messages[0]["content"]]}
    )
    await user_message.create()
    answer = await chat(QARequest(messages=data.messages))
    system_message = Message(
        conversation_id=id,
        author={"role": AuthorTypeEnum.system},
        content={"content_type": ContentTypeEnum.text, "parts": [answer]}
    )
    await system_message.create()
    await Conversation.find_one(Conversation.id == id).update({ "$set": { Conversation.updated_at: datetime.now() }})
    return system_message


async def retrieve_conversation(id: UUID) -> Conversation:
    conversation = await Conversation.get(id)
    if conversation:
        return conversation


async def update_conversation_data(id: UUID, data: dict) -> Union[bool, Conversation]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    conversation = await Conversation.get(id)
    if conversation:
        await conversation.update(update_query)
        return conversation
    return False
