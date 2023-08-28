from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_folder: str = "upload_folder"
    openai_api_key: str = "key"

    class Config:
        env_file = ".env"
        from_attributes = True