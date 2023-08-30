from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from api.models.feedback import RatingEnum, TagEnum

class AddFeedbackDto(BaseModel):
    conversation_id: UUID
    message_id: UUID
    rating: RatingEnum
    tags: Optional[List[TagEnum]]
    text: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "d24beb19-6a51-485d-962f-fd963541f49a",
                "message_id": "7218eb2d-d844-4cab-8349-1b44f8bb8485",
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
