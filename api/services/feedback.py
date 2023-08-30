from uuid import UUID
from typing import Union

from api.models.feedback import Feedback
from api.schemas.feedback import *


feedback_collection = Feedback


async def add_feedback(data: AddFeedbackDto) -> Feedback:
    new_feedback = Feedback(
        conversation_id=data.conversation_id,
        message_id=data.message_id,
        rating=data.rating,
        tags=data.tags,
        text=data.text
    )
    feedback = await new_feedback.create()
    return feedback


async def update_feedback_data(id: UUID, data: UpdateFeedbackDto) -> Union[bool, Feedback]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    feedback = await feedback_collection.get(id)
    if feedback:
        await feedback.update(update_query)
        return await feedback_collection.get(id)
    return False
