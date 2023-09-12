from fastapi import APIRouter
from fastapi_paginate import Page, paginate
from typing import Union

from api.models.feedback import Feedback, RatingEnum
from api.services.feedback import retrieve_feedbacks


router = APIRouter()


@router.get("/feedbacks", response_model=Page[Feedback])
async def get_feedbacks(search: Union[str, None] = None, rating: Union[RatingEnum, None] = None):
    feedbacks = await retrieve_feedbacks(search, rating)
    return paginate(feedbacks)
