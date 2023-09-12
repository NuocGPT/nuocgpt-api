from fastapi import Body, HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta

from api.auth.jwt_handler import sign_jwt
from api.models.user import RoleEnum, User
from api.schemas.auth import *
from config.constants import ErrorMessage
from api.services.mail import send_otp, send_otp_forgot_password
from api.utils.string import generateOTP
from config.config import Settings


hash_helper = CryptContext(schemes=["bcrypt"])


async def user_signin(data: SignInDto = Body(...)):
    user = await User.find_one(User.email == data.email)
    if user:
        if not user.is_verified:
            verify_code = generateOTP(6)
            await user.update({"$set": { "verify_code": verify_code, "verify_code_expire": datetime.now() + timedelta(minutes=Settings().SMTP_OTP_EXPIRES_MINUTES) }})
            send_otp(user.email, verify_code)
            raise HTTPException(status_code=403, detail=ErrorMessage.USER_NOT_VERIFIED)

        password = hash_helper.verify(data.password, user.password)
        if password:
            return {"access_token": sign_jwt(str(user.id)), "roles": user.roles}

        raise HTTPException(status_code=401, detail=ErrorMessage.INCORRECT_EMAIL_OR_PASSWORD)

    raise HTTPException(status_code=401, detail=ErrorMessage.INCORRECT_EMAIL_OR_PASSWORD)


async def user_signup(data: SignUpDto = Body(...)):
    user_exists = await User.find_one(User.email == data.email)
    if user_exists:
        raise HTTPException(
            status_code=401, detail=ErrorMessage.EMAIL_ALREADY_EXISTS
        )

    data.password = hash_helper.encrypt(data.password)
    verify_code = generateOTP(6)
    new_user = User(
        email=data.email,
        password=data.password,
        roles=[RoleEnum.user],
        verify_code=verify_code,
        verify_code_expire=datetime.now() + timedelta(minutes=Settings().SMTP_OTP_EXPIRES_MINUTES),
        created_at=datetime.now()
    )

    user = await new_user.create()
    send_otp(user.email, verify_code)
    return {"id": user.id, "email": user.email}


async def verify_otp(data: VerifyOTPDto = Body(...)):
    user = await User.find_one(User.email == data.email)
    if not user:
        raise HTTPException(status_code=401, detail=ErrorMessage.USER_NOT_FOUND)

    if user.verify_code == data.verify_code and user.verify_code_expire >= datetime.now():
        await user.update({"$set": { "is_verified": True }})
        return {"access_token": sign_jwt(str(user.id)), "roles": user.roles}

    raise HTTPException(status_code=401, detail=ErrorMessage.OTP_INCORRECT_OR_EXPIRED)


async def resend_verify_otp(data: SendVerifyOTPDto = Body(...)):
    user = await User.find_one(User.email == data.email)
    if not user:
        raise HTTPException(status_code=401, detail=ErrorMessage.USER_NOT_FOUND)

    verify_code = generateOTP(6)
    await user.update({"$set": { "verify_code": verify_code, "verify_code_expire": datetime.now() + timedelta(minutes=Settings().SMTP_OTP_EXPIRES_MINUTES) }})
    send_otp(user.email, verify_code)
    return True


async def send_email_forgot_password(data: SendVerifyOTPDto = Body(...)):
    user = await User.find_one(User.email == data.email)
    if user:
        verify_code = generateOTP(6)
        await user.update({"$set": { "verify_code": verify_code, "verify_code_expire": datetime.now() + timedelta(minutes=Settings().SMTP_OTP_EXPIRES_MINUTES) }})
        send_otp_forgot_password(user.email, verify_code)
    
    return True


async def verify_otp_forgot_password(data: VerifyOTPDto = Body(...)):
    user = await User.find_one(User.email == data.email)
    if not user:
        raise HTTPException(status_code=401, detail=ErrorMessage.USER_NOT_FOUND)

    if user.verify_code == data.verify_code and user.verify_code_expire >= datetime.now():
        verify_token = generateOTP(24)
        await user.update({"$set": { "verify_token": verify_token }})
        return {"verify_token": verify_token}

    raise HTTPException(status_code=401, detail=ErrorMessage.OTP_INCORRECT_OR_EXPIRED)


async def add_new_password(data: ForgotPasswordDto = Body(...)):
    user = await User.find_one(User.verify_token == data.verify_token)
    if not user or user.verify_code_expire <= datetime.now():
        raise HTTPException(status_code=401, detail=ErrorMessage.TOKEN_INVALID_OR_EXPIRED)
    
    password = hash_helper.encrypt(data.password)
    await user.update({"$set": { "password": password }})
    return True
