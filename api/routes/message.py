from fastapi import APIRouter, Body

from api.services.conversation import *
from api.schemas.conversation import *


router = APIRouter()


@router.post("")
async def post_message_data(data: AddMessageDto = Body(...)):
    return await post_messages(data)
