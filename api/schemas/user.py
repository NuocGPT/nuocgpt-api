from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

from api.models.user import RoleEnum

class UserResponse(BaseModel):
    email: Optional[EmailStr]
    phone_number: Optional[str]
    roles: List[RoleEnum]

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@enosta.com",
            }
        }
