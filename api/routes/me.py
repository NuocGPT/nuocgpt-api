from fastapi import APIRouter, Depends
from typing import Annotated

from api.auth.jwt_handler import get_user_id
from api.services.user import *
from api.schemas.user import *


router = APIRouter()


@router.get("", response_model=UserResponse)
async def add_feedback_data(user_id: Annotated[dict, Depends(get_user_id)]):
    return await retrieve_user(user_id)
