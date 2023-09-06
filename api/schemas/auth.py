from uuid import UUID
from pydantic import BaseModel, EmailStr

class SignInDto(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
                "password": "3xt3m#",
            }
        }


class SignUpDto(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
                "password": "3xt3m#",
            }
        }


class VerifyOTPDto(BaseModel):
    email: EmailStr
    verify_code: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
                "verify_code": "095648",
            }
        }


class ResendVerifyOTPDto(BaseModel):
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
            }
        }


class Token(BaseModel):
    user_id: UUID
    expires: float

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "0321b384-1e67-43b6-b723-3389b19a761e",
                "expires": "1693900575"
            }
        }
