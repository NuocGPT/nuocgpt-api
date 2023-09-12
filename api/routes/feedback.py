from fastapi import APIRouter, Body, Depends
from uuid import UUID
from typing import Annotated, Union

from api.auth.jwt_handler import get_user_id
from api.models.feedback import Feedback
from api.schemas.feedback import AddFeedbackDto, UpdateFeedbackDto
from api.services.feedback import add_feedback, update_feedback_data

router = APIRouter()


@router.post("", response_model=Feedback)
async def add_feedback_data(user_id: Annotated[dict, Depends(get_user_id)], data: AddFeedbackDto = Body(...)):
    return await add_feedback(user_id, data)


@router.put("/{id}", response_model=Union[bool, Feedback])
async def update_feedback(id: UUID, req: UpdateFeedbackDto = Body(...)):
    return await update_feedback_data(id, req.dict())
