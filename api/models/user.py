from uuid import UUID, uuid4
from beanie import Document
from pydantic import EmailStr, Field, ConfigDict


class User(Document):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    password: str

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                "email": "sample@nuocgpt.com",
                "password": "$2y$10$qVG8JaWgzo75ZPU1EpB6Xu.cbwvds5g/VlyZypU1kQruw7bIR0Vfy",
            }
        }

    class Settings:
        name = "users"
