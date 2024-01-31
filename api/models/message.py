from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import UUID4, BaseModel, Field


class AuthorTypeEnum(str, Enum):
    user = "user"
    system = "system"


class Author(BaseModel):
    id: Optional[UUID]
    role: AuthorTypeEnum


class ContentTypeEnum(str, Enum):
    text = "text"


class Content(BaseModel):
    content_type: ContentTypeEnum
    parts: List[str]

    class Config:
        arbitrary_types_allowed = True


class Message(Document):
    id: UUID4 = Field(default_factory=uuid4)
    conversation_id: UUID4
    question_id: Optional[UUID4] = None
    author: Author
    content: Content
    created_at: datetime = datetime.now()

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                "conversation_id": "d24beb19-6a51-485d-962f-fd963541f49a",
                "author": {
                    "id": "fd7a4aad-d39f-47bc-a10a-971135bcdd3b",
                    "role": "user",
                },
                "content": {
                    "content_type": "text",
                    "parts": ["Hello! How can I assist you today?"],
                },
            }
        }

    class Settings:
        name = "messages"
