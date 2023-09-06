from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient


import api.models as models
from config.config import Settings


async def initiate_database():
    client = AsyncIOMotorClient(Settings().DATABASE_URL)
    await init_beanie(
        database=client.get_default_database(), document_models=models.__all__
    )
