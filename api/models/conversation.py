from typing import Optional
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from datetime import datetime


class Conversation(Document):
    id: UUID = Field(default_factory=uuid4)
    title: Optional[str] = None
    author_id: UUID
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                "title": "Assist with user query.",
                "author_id": "d24beb19-6a51-485d-962f-fd963541f49a",
            }
        }

    class Settings:
        name = "conversations"
