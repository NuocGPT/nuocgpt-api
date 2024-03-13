from uuid import UUID, uuid4
from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class RatingEnum(str, Enum):
    thumbs_up = 'thumbsUp'
    thumbs_down = 'thumbsDown'

class TagEnum(str, Enum):
    harmful = 'harmful'
    false = 'false'
    not_helpful = 'not-helpful'


class FeedbackConversation(BaseModel):
    id: Optional[UUID] = None
    title: str


class FeedbackQuestion(BaseModel):
    id: Optional[UUID] = None
    content: str


class FeedbackMessage(BaseModel):
    id: Optional[UUID] = None
    content: str


class FeedbackUser(BaseModel):
    id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class Feedback(Document):
    id: UUID = Field(default_factory=uuid4)
    conversation: FeedbackConversation
    question: FeedbackQuestion
    message: FeedbackMessage
    user: Optional[FeedbackUser] = None
    rating: RatingEnum
    tags: Optional[List[TagEnum]] = None
    text: Optional[str] = None
    created_at: datetime = datetime.now()

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                "conversation": {
                    "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                    "title": "string"
                },
                "question": {
                    "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                    "content": "string"
                },
                "message": {
                    "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                    "content": "string"
                },
                "user": {
                    "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                    "email": "string@enosta.com"
                },
                "rating": "thumbsDown",
                "tags": ["harmful"],
                "text": "the answer isn't correct"
            }
        }

    class Settings:
        name = "feedbacks"
