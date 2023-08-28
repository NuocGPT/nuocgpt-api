from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class AddConversationDto(BaseModel):
    title: Optional[str] = None
    author_id: UUID
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Assist with user query.",
                "author_id": "d24beb19-6a51-485d-962f-fd963541f49a",
                "message": "Hello!"
            }
        }

class AddMessageDto(BaseModel):
    message: str
    author_id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "author_id": "d24beb19-6a51-485d-962f-fd963541f49a",
                "message": "Hello!"
            }
        }
