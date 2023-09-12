from fastapi import APIRouter
from fastapi_paginate import Page, paginate
from typing import Union

from api.models.feedback import Feedback, RatingEnum
from api.schemas.feedback import CountRatingResponse
from api.services.feedback import retrieve_feedbacks, count_ratings


router = APIRouter()


@router.get("/feedbacks", response_model=Page[Feedback])
async def get_feedbacks(search: Union[str, None] = None, rating: Union[RatingEnum, None] = None):
    feedbacks = await retrieve_feedbacks(search, rating)
    return paginate(feedbacks)


@router.get("/count-ratings", response_model=CountRatingResponse)
async def count_status_ratings():
    return await count_ratings()
