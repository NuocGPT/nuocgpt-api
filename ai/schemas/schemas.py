from typing import Annotated
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
    question: str
    messages: list = Body(None, description="List of chat history")
    language: str = Body("English", description="Language of expected response")
    metadata: list = Body([], description="List of metadata")
