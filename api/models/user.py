from enum import Enum
from typing import List
from uuid import UUID, uuid4
from beanie import Document, Indexed
from pydantic import EmailStr, Field
from datetime import datetime, timedelta

from config.config import Settings


class RoleEnum(str, Enum):
    user = 'user'
    admin = 'admin'


class User(Document):
    id: UUID = Field(default_factory=uuid4)
    email: Indexed(EmailStr, unique=True)
    password: str
    roles: List[RoleEnum] = [RoleEnum.user]
    is_verified: bool = False
    verify_code: str = None
    verify_code_expire: datetime = datetime.now() + timedelta(minutes=Settings().SMTP_OTP_EXPIRES_MINUTES)
    verify_token: str = None
    created_at: datetime = datetime.now()

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
