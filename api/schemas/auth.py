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


class SendVerifyOTPDto(BaseModel):
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


class ForgotPasswordDto(BaseModel):
    verify_token: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "verify_token": "567345938456",
                "password": "enosta@123",
            }
        }


class PhoneNumberSignInDto(BaseModel):
    phone_number: str

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+84987654321",
            }
        }


class ReSendSMSVerifyOTPDto(BaseModel):
    phone_number: str

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+84911793246",
            }
        }


class SmsVerifyOTPDto(BaseModel):
    phone_number: str
    verify_code: str

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+84911793246",
                "verify_code": "095648",
            }
        }
