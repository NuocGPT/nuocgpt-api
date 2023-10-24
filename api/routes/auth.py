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


@router.get("/user-seeding")
async def user_seeding():
    return await seeding()


@router.post("/verify-otp")
async def verify_otp_verification(data: VerifyOTPDto = Body(...)):
    return await verify_otp(data)


@router.post("/resend-verify-otp")
async def resend_verify_otp_verification(data: SendVerifyOTPDto = Body(...)):
    return await resend_verify_otp(data)


@router.post("/send-verify-otp-forgot-password")
async def verify_forgot_password(data: SendVerifyOTPDto = Body(...)):
    return await send_email_forgot_password(data)


@router.post("/verify-otp-forgot-password")
async def verify_fotgot_password(data: VerifyOTPDto = Body(...)):
    return await verify_otp_forgot_password(data)


@router.post("/new-password-forgot-password")
async def add_new_password_data(data: ForgotPasswordDto = Body(...)):
    return await add_new_password(data)
