from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_folder: str = "upload_folder"
    openai_api_key: str = "key"
    aws_secret_access_key: str = "aws_secret_access_key"
    aws_access_key: str = "aws_access_key"

    class Config:
        env_file = ".env"
        from_attributes = True