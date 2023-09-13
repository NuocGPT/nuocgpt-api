from typing import List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from api.models.user import RoleEnum

class UserResponse(BaseModel):
    email: EmailStr
    roles: List[RoleEnum]

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
            }
        }
