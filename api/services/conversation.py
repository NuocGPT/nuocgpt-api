from typing import List, Union
from uuid import UUID

from api.models.conversation import Conversation
from api.models.message import Message, AuthorTypeEnum, ContentTypeEnum
from api.schemas.conversation import *

conversation_collection = Conversation
message_collection = Message



async def retrieve_conversations() -> List[Conversation]:
    conversations = await conversation_collection.all().sort("-updated_at").to_list()
    return conversations


async def add_conversation(data: AddConversationDto) -> Conversation:
    new_conversation = Conversation(title=data.title, author_id=data.author_id)
    conversation = await new_conversation.create()
    new_message = Message(
        conversation_id=conversation.id,
        author={"id": data.author_id, "role": AuthorTypeEnum.user},
        content={"content_type": ContentTypeEnum.text, "parts": [data.message]}
    )
    await new_message.create()
    return conversation


async def retrieve_messages(id) -> List[Message]:
    messages = await message_collection.find(Message.conversation_id == id).sort("-created_at").to_list()
    return messages


async def add_message(id: UUID, data: AddMessageDto) -> Message:
    new_message = Message(
        conversation_id=id,
        author={"id": data.author_id, "role": AuthorTypeEnum.user},
        content={"content_type": ContentTypeEnum.text, "parts": [data.message]}
    )
    return await new_message.create()


async def retrieve_conversation(id: UUID) -> Conversation:
    conversation = await conversation_collection.get(id)
    if conversation:
        return conversation


async def update_conversation_data(id: UUID, data: dict) -> Union[bool, Conversation]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    conversation = await conversation_collection.get(id)
    if conversation:
        await conversation.update(update_query)
        return conversation
    return False
