from datetime import datetime, timedelta
from typing import List, Union
from uuid import UUID
from fastapi.responses import StreamingResponse
import time
from langdetect import detect

from ai.routes.chat import stream_chat
from ai.routes.summarize import summarize
from ai.schemas.schemas import QARequest
from api.models.conversation import Conversation
from api.models.message import AuthorTypeEnum, ContentTypeEnum, Message
from api.schemas.conversation import *
from config.constants import IrrelevantMessage, irrelevant_keywords


async def retrieve_conversations(user_id: UUID) -> List[Conversation]:
    conversations = (
        await Conversation.find(Conversation.author_id == user_id)
        .sort("-updated_at")
        .to_list()
    )
    return conversations


async def reject_stream(text: str):
    for i in [text[i:i+4] for i in range(0, len(text), 4)]:
        yield i
        time.sleep(0.05)


async def post_messages(data: AddConversationDto) -> Message:
    if any(
        substring.lower() in data.message.lower() for substring in irrelevant_keywords
    ):
        lang = detect(data.message)
        answer = IrrelevantMessage.VI if lang == "vi" else IrrelevantMessage.EN
        return StreamingResponse(reject_stream(answer), media_type='text/event-stream')
    else:
        body = QARequest(messages=[{"role": "user", "content": data.message}])
        return await stream_chat(body)


async def add_conversation(user_id: UUID, data: AddConversationDto) -> Conversation:
    new_conversation = Conversation(
        title=data.title,
        author_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    conversation = await new_conversation.create()
    user_message = Message(
        conversation_id=conversation.id,
        author={"id": user_id, "role": AuthorTypeEnum.user},
        content={"content_type": ContentTypeEnum.text, "parts": [data.message]},
        created_at=datetime.now() - timedelta(seconds=20),
    )
    await user_message.create()
    return conversation


async def retrieve_messages(id) -> List[Message]:
    messages = (
        await Message.find(Message.conversation_id == id).sort("-created_at").to_list()
    )
    return messages


def convert_messages(message: Message):
    return {"role": message.author.role, "content": message.content.parts[0]}


async def add_message(id: UUID, user_id: UUID, data: AddMessageDto):
    user_message = Message(
        conversation_id=id,
        author={"id": user_id, "role": AuthorTypeEnum.user},
        content={"content_type": ContentTypeEnum.text, "parts": [data.message]},
        created_at=datetime.now(),
    )
    await user_message.create()
    messages = (
        await Message.find(Message.conversation_id == id).sort("created_at").to_list()
    )

    if any(
        substring.lower() in data.message.lower() for substring in irrelevant_keywords
    ):
        lang = detect(data.message)
        answer = IrrelevantMessage.VI if lang == "vi" else IrrelevantMessage.EN
        return StreamingResponse(reject_stream(answer), media_type='text/event-stream')
    else:
        body = QARequest(
            messages=[
                {"role": m.author.role, "content": m.content.parts[0]} for m in messages
            ]
        )
        return await stream_chat(body)


async def add_answer(id: UUID, data: AddAnswerDto) -> Message:
    system_message = Message(
        conversation_id=id,
        author={"role": AuthorTypeEnum.system},
        content={"content_type": ContentTypeEnum.text, "parts": [data.answer]},
        created_at=datetime.now(),
    )
    return await system_message.create()


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


async def delete_conversation_data(id: UUID) -> Union[bool, Conversation]:
    await Message.find(Message.conversation_id == id).delete()
    await Conversation.find_one(Conversation.id == id).delete()
    return True


async def summarize_question(id: UUID) -> Union[bool, Conversation]:
    messages = (
        await Message.find(Message.conversation_id == id).sort("created_at").to_list()
    )
    title = await summarize(messages[0].content.parts[0])
    return await update_conversation_data(id, {"title": title})


async def update_feedback_data(
    id: UUID, data: UpdateConversationDto
) -> Union[bool, Conversation]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    feedback = await Conversation.get(id)
    if feedback:
        await feedback.update(update_query)
        return await Conversation.get(id)
    return False
