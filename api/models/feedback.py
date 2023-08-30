from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
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


class Feedback(Document):
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    message_id: UUID
    user_id: Optional[UUID]
    rating: RatingEnum
    tags: Optional[List[TagEnum]]
    text: Optional[str]
    created_at: datetime = datetime.now()

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                "conversation_id": "d24beb19-6a51-485d-962f-fd963541f49a",
                "message_id": "7218eb2d-d844-4cab-8349-1b44f8bb8485",
                "user_id": "f1f2b76a-a1db-45e2-941d-49efc0ab62fa",
                "rating": "thumbsDown",
                "tags": ["harmful"],
                "text": "the answer isn't correct"
            }
        }

    class Settings:
        name = "feedbacks"
