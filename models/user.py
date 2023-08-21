from typing import Optional, Any

from beanie import Document
from pydantic import BaseModel, EmailStr


class User(Document):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@nuocgpt.com",
                "password": "$2y$10$qVG8JaWgzo75ZPU1EpB6Xu.cbwvds5g/VlyZypU1kQruw7bIR0Vfy",
            }
        }

    class Settings:
        name = "user"


class UpdateUserModel(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]

    class Collection:
        name = "user"

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@nuocgpt.com",
                "password": "$2y$10$qVG8JaWgzo75ZPU1EpB6Xu.cbwvds5g/VlyZypU1kQruw7bIR0Vfy",
            }
        }


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation successful",
                "data": "Sample data",
            }
        }
