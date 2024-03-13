from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from api.models.feedback import RatingEnum, TagEnum, FeedbackConversation, FeedbackMessage, FeedbackQuestion

class AddFeedbackDto(BaseModel):
    conversation: FeedbackConversation
    question: FeedbackQuestion
    message: FeedbackMessage
    rating: RatingEnum
    tags: Optional[List[TagEnum]]  = None
    text: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "conversation": {
                    "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                    "title": "string"
                },
                "message": {
                    "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                    "content": "string"
                },
                "rating": "thumbsDown",
                "tags": ["harmful"],
                "text": "the answer isn't correct"
            }
        }


class UpdateFeedbackDto(BaseModel):
    tags: Optional[List[TagEnum]]
    text: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["harmful"],
                "text": "the answer isn't correct"
            }
        }


class CountRatingResponse(BaseModel):
    likes: int
    dis_likes: int
