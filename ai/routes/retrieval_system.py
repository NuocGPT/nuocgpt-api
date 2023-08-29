import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from config.config import Settings

import os

from schemas.schemas import ImportFileRequest, ImportMultipleFilesRequest
from core.data_ingestor import DataIngestor
from core.constants import IngestDataConstants

OPENAI_API_KEY = Settings().OPENAI_API_KEY
print('OPENAI_API_KEY')
print(OPENAI_API_KEY)
MAX_FILE_SIZE = IngestDataConstants.MAX_FILE_SIZE
ALLOWED_EXTENSIONS = IngestDataConstants.ALLOWED_EXTENSIONS

router = APIRouter()

@router.post("/import-file")
async def import_file(request: ImportFileRequest = Depends()):
    file = request.file
    lang = request.lang

    file_size = os.fstat(file.file.fileno()).st_size

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the allowed limit")
    
    file_extension = os.path.splitext(file.filename)[1][1:].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF, CSV, TXT and XLSX files are allowed.",
        )
    
    data_ingestor = DataIngestor(lang=lang)
    data_ingestor_fn = {
        "pdf": data_ingestor.ingest_pdf,
        "json": data_ingestor.ingest_json
    }

    try:
        file_path = os.path.join(IngestDataConstants.TEMP_UPLOADED_FOLDER, "temp." + file_extension)

        with open(file_path, "wb", encoding='utf-8') as f:
            contents = await file.read()
            f.write(contents)

        metadata = data_ingestor_fn[file_extension](file_path)
        metadata = {} if metadata is None else metadata

    except Exception as e:
        return JSONResponse(status_code=500, content={"errorCode": 500, "errorMessage": e})
    
    return JSONResponse(status_code=200, content={"Add Document To VectorDB Successfully!"})

@router.post("/import-multi-files")
async def import_multi_files(
    request: ImportMultipleFilesRequest=Depends()
):
    files = request.files
    lang = request.lang

    try:
        for file in files:
            import_file_request = ImportFileRequest(file=file, lang = lang)
            await import_file(request=import_file_request)
    except Exception as e:
        return JSONResponse(status_code=500, content={"errorCode": 500, "errorMessage": e})
    
    return JSONResponse(status_code=200, content={"Add Document To VectorDB Successfully!"})
