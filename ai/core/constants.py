import os
from typing import Dict, Type, Union
from langchain.llms import BaseLLM, type_to_cls_dict
from langchain.chat_models import ChatOpenAI
from configs.config import Settings


class BaseConstants:
    ROOT_PATH = os.path.abspath(os.path.join(__file__, "../.."))

class IngestDataConstants(BaseConstants):
    CHUNK_SIZE = 4000
    CHUNK_OVERLAP = 500
    TEMP_DB_FOLDER = '/tmp/vectorstores/'
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS = ["pdf", "json"]
    TEMP_UPLOADED_FOLDER = '/tmp/uploaded/'

class LangChainOpenAIConstants(BaseConstants):
    type_to_cls_dict_plus: Dict[str, Type[Union[BaseLLM, ChatOpenAI]]] = {k: v for k, v in type_to_cls_dict.items()}
    type_to_cls_dict_plus.update({"chat_openai": ChatOpenAI})
    AGENT_SYSTEM_PROMPT_CONTENT = (
        "Do your best to answer the questions. "
        "Feel free to use any tools available to look up relevant information, only if necessary"
    )
    KNOWLEDGE_BASE_RETRIEVER_NAME: str = "knowledge_base_retriever"
    KNOWLEDGE_BASE_RETRIEVER_DESCRIPTION: str = (
        "Searches and returns documents in the knowledge base"
    )


class AWSConstants(BaseConstants):
    AWS_ACCESS_KEY = Settings().aws_access_key
    AWS_SECRET_ACCESS_KEY = Settings().aws_secret_access_key
    REGION_NAME = Settings().aws_region
    S3_BUCKET = Settings().aws_bucket
