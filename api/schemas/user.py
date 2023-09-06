from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
            }
        }
