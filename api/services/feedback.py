from uuid import UUID
from typing import Union
from datetime import datetime

from api.models.feedback import Feedback, FeedbackQuestion, FeedbackUser
from api.models.user import User
from api.models.message import Message
from api.schemas.feedback import *
from beanie.odm.operators.find.logical import Or


async def add_feedback(user_id: UUID, data: AddFeedbackDto) -> Feedback:
    user = await User.get(user_id)
    message = await Message.get(data.message.id)
    if message.question_id:
        question = await Message.get(message.question_id)
    else:
        messages = await Message.find(Message.conversation_id==data.conversation.id).sort("created_at").to_list()
        for idx, m in enumerate(messages):
            if str(m.id) == str(data.message.id):
                question = messages[idx - 1]
                break
    new_feedback = Feedback(
        conversation=data.conversation,
        question=FeedbackQuestion(id=question.id, content=question.content.parts[0]),
        message=data.message,
        rating=data.rating,
        tags=data.tags,
        text=data.text,
        user=FeedbackUser(id=user.id, email=user.email),
        created_at=datetime.now()
    )
    feedback = await new_feedback.create()
    return feedback


async def update_feedback_data(id: UUID, data: UpdateFeedbackDto) -> Union[bool, Feedback]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    feedback = await Feedback.get(id)
    if feedback:
        await feedback.update(update_query)
        return await Feedback.get(id)
    return False


async def retrieve_feedbacks(search: str, rating: RatingEnum) -> List[Feedback]:
    search_criteria = []
    if search:
        search_criteria.append(
            Or(
                Feedback.question.content=={ "$regex": search, "$options": 'i' },
                Feedback.message.content=={ "$regex": search, "$options": 'i' }
            )
        )
    if rating:
        search_criteria.append(Feedback.rating==rating)

    feedbacks = await Feedback.find(*search_criteria).sort("-created_at").to_list()
    return feedbacks


async def count_ratings():
    likes = await Feedback.find(Feedback.rating==RatingEnum.thumbs_up).count()
    dis_likes = await Feedback.find(Feedback.rating==RatingEnum.thumbs_down).count()
    return {"likes": likes, "dis_likes": dis_likes}
