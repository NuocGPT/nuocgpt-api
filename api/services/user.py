from uuid import UUID

from fastapi import HTTPException

from api.models.user import User
from api.schemas.user import UserResponse
from config.constants import ErrorMessage

async def retrieve_user(user_id: UUID) -> UserResponse:
    user = await User.get(user_id)
    if user:
        return user
    
    raise HTTPException(status_code=401, detail=ErrorMessage.USER_NOT_FOUND)
