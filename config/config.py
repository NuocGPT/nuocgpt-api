from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database configurations
    DATABASE_URL: Optional[str] = None

    # JWT
    SECRET_KEY: str = "secret"
    algorithm: str = "HS256"

    # AI
    OPENAI_API_KEY: str = "key"
    AWS_SECRET_ACCESS_KEY: str = "aws_secret_access_key"
    AWS_ACCESS_KEY: str = "aws_access_key"
    AWS_S3_BUCKET: str = "aws_bucket"
    AWS_REGION: str = "aws_region"
    LANGCHAIN_API_KEY: str = "langchain_api_key"
    LANGCHAIN_ENDPOINT: str = "langchain_endpoint"
    LANGCHAIN_TRACING_V2: str = "is_tracing"
    LANGCHAIN_PROJECT: str = "project"
    REDIS_URL: str = "redis"

    # Mail
    SMTP_HOST: str = "smtp_host"
    SMTP_PORT: str = "smtp_port"
    SMTP_USER: str = "smtp_user"
    SMTP_PASS: str = "smtp_pass"
    SMTP_OTP_EXPIRES_MINUTES: int = 5

    # Twilio
    TWILIO_ACCOUNT_SID: str = "twilio_account_sid"
    TWILIO_AUTH_TOKEN: str = "twilio_auth_token"

    class Config:
        env_file = ".env"
        from_attributes = True
