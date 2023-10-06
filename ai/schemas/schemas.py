from typing import Annotated, Optional
from fastapi import Body, File, UploadFile
from pydantic import BaseModel

class ImportFileRequest(BaseModel):
    file: Annotated[
        UploadFile,
        File(..., description="The file of knowledge base in pdf or json format"),
    ]
    lang: str

class ImportMultipleFilesRequest(BaseModel):
    files: Annotated[
        list[UploadFile], File(..., description="Multiple files for knowledge base in pdf or json format. WARNING: USING THE SAME LANGUAGE!!!")
    ]
    lang: str

class QARequest(BaseModel):
    """Request schema for QA. Chat history format:
    [
        {
            "role": "Role",
            "content": "content",    
        },
        {
            "role": "Role",
            "content": "content",    
        }
    ]"""
    messages: list = Body(None, description="List of chat history")
    language:  Optional[str] = Body(None, description="Language of expected response")
    metadata: Optional[list] = Body([], description="List of metadata")


class ImportSensorDataRequest(BaseModel):
    """
    Data format:
    "questions": [
        {
            "id": "000003eb-8db0-4de6-86c6-23d9cd2c9832",
            "question": "question 1"
        }
    ]
    """
    questions: list = Body(None, description="list of questions with ids")
