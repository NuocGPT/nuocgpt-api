from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID


class SensorDataLib(Document):
    id: UUID = Field(default_factory=uuid4)
    question: str
    answer: str
    parameter: str
    location: str
    value: float
    unit: str
    time: datetime

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "aaa23890-6d64-46e3-a60c-00f08c5fd51e",
                "question": "question",
                "answer": "answer",
                "parameter": "parameter",
                "location": "location",
                "value": 0,
                "unit": "unit"
            }
        }

    class Settings:
        name = "sensor_data_lib"

    
