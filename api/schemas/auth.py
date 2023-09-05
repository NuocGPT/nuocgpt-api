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
