from fastapi import APIRouter, Body
from uuid import UUID
from typing import Union

from api.schemas.auth import *
from api.services.auth import *


router = APIRouter()


@router.post("/sign-in")
async def sign_in(data: SignInDto = Body(...)):
    return await user_signin(data)


@router.post("/sign-up")
async def sign_up(data: SignInDto = Body(...)):
    return await user_signup(data)


@router.post("/verify-otp")
async def verify_otp_verification(data: VerifyOTPDto = Body(...)):
    return await verify_otp(data)


@router.post("/resend-verify-otp")
async def resend_verify_otp_verification(data: ResendVerifyOTPDto = Body(...)):
    return await resend_verify_otp(data)
