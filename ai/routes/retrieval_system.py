import logging
from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from config.config import Settings
import csv
import os
import asyncio
from ai.schemas.schemas import ImportFileRequest, ImportMultipleFilesRequest, ImportSensorDataRequest
from ai.core.data_ingestor import DataIngestor
from ai.core.constants import IngestDataConstants

OPENAI_API_KEY = Settings().OPENAI_API_KEY
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

@router.post("/import-sensor-data-question")
async def import_sensor_data_question(question: str, id: str):
    data_ingestor = DataIngestor()
    try:
        data_ingestor.load_sensor_data_question(question, id)
    except Exception as e:
        logging.error(e)

async def import_data():
    try:
        with open('files/sensordata.csv', 'r', encoding='utf-8') as file:
            csvreader = csv.reader(file)
            data = []
            for row in csvreader:
                data.append({"id": row[0], "question": row[1]})

        for idx, question in enumerate(data):
            print("INDEX", idx)
            await import_sensor_data_question(question["question"], question["id"])
        print("DONE")
    except Exception as e:
        logging.error(e)

def add_data():
    asyncio.run(import_data())

@router.post("/import-sensor-data-lib")
async def import_sensor_data_lib(background_tasks: BackgroundTasks=BackgroundTasks()):
    background_tasks.add_task(add_data)
    return {"status": True}
