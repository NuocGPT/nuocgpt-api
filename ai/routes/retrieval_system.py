import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime

import qdrant_client
from ai.core.constants import IngestDataConstants, LangChainOpenAIConstants
from ai.core.data_ingestor import DataIngestor
from ai.llm.base_model.langchain_openai import openai_embedding_with_backoff
from ai.schemas.schemas import ImportFileRequest, ImportMultipleFilesRequest
from config.config import Settings
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain_community.vectorstores.qdrant import Qdrant

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
        raise HTTPException(
            status_code=413, detail="File size exceeds the allowed limit"
        )

    file_extension = os.path.splitext(file.filename)[1][1:].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF, CSV, TXT and XLSX files are allowed.",
        )

    data_ingestor = DataIngestor(lang=lang)
    data_ingestor_fn = {
        "pdf": data_ingestor.ingest_pdf,
        "json": data_ingestor.ingest_json,
    }

    try:
        file_path = os.path.join(
            IngestDataConstants.TEMP_UPLOADED_FOLDER, "temp." + file_extension
        )

        if not os.path.exists(IngestDataConstants.TEMP_UPLOADED_FOLDER):
            os.makedirs(IngestDataConstants.TEMP_UPLOADED_FOLDER)

        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        metadata = data_ingestor_fn[file_extension](file_path)
        metadata = {} if metadata is None else metadata

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"errorCode": 500, "errorMessage": e}
        )

    return JSONResponse(
        status_code=200, content={"message": "Add Document To VectorDB Successfully!"}
    )


@router.post("/import-multi-files")
async def import_multi_files(request: ImportMultipleFilesRequest = Depends()):
    files = request.files
    lang = request.lang

    try:
        for file in files:
            import_file_request = ImportFileRequest(file=file, lang=lang)
            await import_file(request=import_file_request)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"errorCode": 500, "errorMessage": e}
        )

    return JSONResponse(
        status_code=200, content={"Add Document To VectorDB Successfully!"}
    )


@router.post("/import-sensor-data-question")
async def import_sensor_data_question(question: str, id: str):
    data_ingestor = DataIngestor()
    try:
        data_ingestor.load_sensor_data_question(question, id)
    except Exception as e:
        logging.error(e)


async def import_data():
    root_path = os.path.join(
        LangChainOpenAIConstants.ROOT_PATH,
        "data/JSON",
    )
    vectorstore_path = os.path.join(
        IngestDataConstants.TEMP_DB_FOLDER, "sensor_data_lib"
    )
    # embeddings = openai_embedding_with_backoff()

    # if os.path.exists(f"{vectorstore_path}/meta.json"):
    #     client = qdrant_client.QdrantClient(path=vectorstore_path)
    #     vectorstore = Qdrant(
    #         client=client, collection_name="sensor_data_lib", embeddings=embeddings
    #     )
    # else:
    #     vectorstore = None

    # for file in os.listdir(root_path)[:3]:
    #     path = os.path.join(root_path, file)
    #     docs = []
    #     with open(
    #         path,
    #         encoding="utf-8",
    #     ) as f:
    #         data = json.loads(f.read())

    #     param = data["Parameter"]
    #     location = data["Location"]
    #     unit = data["Unit"]

    #     for obj in data["Data"]:
    #         metadata = {}
    #         metadata["source"] = path

    #         timestamp = datetime.strptime(
    #             re.sub(r"T[0-9][0-9]:[0-9][0-9]:*[0-9]*[0-9]*Z", "", obj.get("Time")),
    #             "%Y-%m-%d",
    #         )
    #         try:
    #             time_to_timestamp = datetime.timestamp(timestamp)
    #             metadata["time"] = time_to_timestamp
    #             metadata["parameter"] = param
    #             metadata["location"] = location
    #             metadata["unit"] = unit

    #             docs.append(Document(page_content=obj["Value"], metadata=metadata))
    #         except Exception as e:
    #             print(f"error in {file}, {obj['Time']}")
    #             pass

    #     text_splitter = TokenTextSplitter(
    #         model_name="gpt-3.5-turbo",
    #         chunk_size=IngestDataConstants.CHUNK_SIZE,
    #         chunk_overlap=IngestDataConstants.CHUNK_OVERLAP,
    #     )

    #     splitted_documents = text_splitter.split_documents(docs)

    #     if vectorstore:
    #         vectorstore.add_documents(splitted_documents)
    #     else:
    #         vectorstore = Qdrant.from_documents(
    #             docs,
    #             embeddings,
    #             path=vectorstore_path,
    #             collection_name="sensor_data_lib",
    #         )

    #     print(f"Ingest succesfully {file}")
    #     time.sleep(30)
    print("DONE")


def add_data():
    asyncio.run(import_data())


@router.post("/import-sensor-data-lib")
async def import_sensor_data_lib(background_tasks: BackgroundTasks = BackgroundTasks()):
    background_tasks.add_task(add_data)
    return {"status": True}
