from fastapi import APIRouter, Body

from database.database import *
from models.user import *

router = APIRouter()


@router.get("/", response_description="Users retrieved", response_model=Response)
async def get_users():
    users = await retrieve_users()
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Users data retrieved successfully",
        "data": users,
    }
