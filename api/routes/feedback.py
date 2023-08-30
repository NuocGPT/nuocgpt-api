from fastapi import APIRouter, Body
from uuid import UUID
from typing import Union

from api.models.feedback import Feedback
from api.schemas.feedback import AddFeedbackDto
from api.services.feedback import *


router = APIRouter()


@router.post("", response_model=Feedback)
async def add_feedback_data(data: AddFeedbackDto = Body(...)):
    return await add_feedback(data)


@router.put("/{id}", response_model=Union[bool, Feedback])
async def update_feedback(id: UUID, req: UpdateFeedbackDto = Body(...)):
    return await update_feedback_data(id, req.dict())
