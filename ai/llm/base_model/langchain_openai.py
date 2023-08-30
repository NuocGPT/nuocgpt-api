import json
import os
import re
from typing import Tuple
from fastapi import HTTPException
import yaml
import openai
import backoff

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain import LLMChain
from langchain.retrievers import MergerRetriever
from langchain.vectorstores import Chroma
from langchain.vectorstores.base import VectorStore
from langchain.embeddings.openai import OpenAIEmbeddings

from ai.llm.data_loader.load_langchain_config import LangChainDataLoader
from ai.core.constants import LangChainOpenAIConstants, IngestDataConstants
from ai.core.aws_service import AWSService
from ai.llm.base_model.retrieval_chain import CustomConversationalRetrievalChain
from ai.core.constants import IngestDataConstants

from config.config import Settings
 
os.environ["OPENAI_API_KEY"] = Settings().OPENAI_API_KEY

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def openai_embedding_with_backoff():
    return OpenAIEmbeddings(chunk_size=IngestDataConstants.CHUNK_OVERLAP)

class LangchainOpenAI:
    """Langchain OpenAI"""
    def __init__(
        self,
        language: str = "English",
        metadata: list[dict] = None,
    ):
        self.output_parser = None
        self.is_chat_model, self.llm_cls, self.llm_model = self.load_llm_model()
        self.data_loader = LangChainDataLoader()
        self.lang = language

        self.data_loader.preprocessing_qa_prompt(
            metadata=self._format_dict_list(metadata or []),
            language=self.lang
        )
        vectorstore_folder_path = os.path.join(IngestDataConstants.TEMP_DB_FOLDER, f"{language}/")
        self.vectorstore, self.vectorstore_retriever = self.get_langchain_retriever(vectorstore_folder_path)
        s3_client = AWSService()
        s3_client.download_from_s3(self.vectorstore)


    def get_chain(self) -> ConversationalRetrievalChain:
        prompt_title = "qaPrompt"

        docs_chain = load_qa_chain(self.llm_model, prompt=self.data_loader.prompts[prompt_title])
        return CustomConversationalRetrievalChain(
            retriever=self.vectorstore.as_retriever()
            if self.vectorstore_retriever is None
            else self.vectorstore_retriever,
            combine_docs_chain=docs_chain,
            question_generator=LLMChain(llm=self.llm_model, prompt=self.data_loader.prompts["condensePrompt"]),
            max_tokens_limit=3500,
            output_parser=self.output_parser,
        )

    @staticmethod
    def load_llm_model():
        with open(
            os.path.join(
                LangChainOpenAIConstants.ROOT_PATH, f"configs/llms/{os.environ.get('PROMPT_VERSION', '280823')}.yaml"
            )
        ) as f:
            model_configs = yaml.safe_load(f)
        model_type = model_configs.pop("_type")
        llm_cls = LangChainOpenAIConstants.type_to_cls_dict_plus[model_type]
        llm_model = llm_cls(**model_configs)
        is_chat_model = isinstance(llm_model, ChatOpenAI)
        return is_chat_model, llm_cls, llm_model
    
    @staticmethod
    def get_langchain_retriever(
        self, vectorstore_folder_path: str, vectorstore_search_kwargs: dict = None
    ) -> Tuple[VectorStore, MergerRetriever]:
        if vectorstore_search_kwargs is None:
            vectorstore_search_kwargs = {"k": 3, "score_threshold": 0.3}

        try:
            embeddings = self.openai_embedding_with_backoff()
            vectorstore = Chroma(persist_directory=vectorstore_folder_path, embedding_function=embeddings)
            
            return vectorstore, vectorstore.as_retriever()
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error when loading vectorstore")
    
    def _detect_language(self, question: str) -> str:
        try:
            language_detect_prompt = self.data_loader.prompts.get("detectLanguagePrompt").template.format(
                question=question,
                chat_history="",
            )
            detected_language = (
                self.llm_model.generate([[HumanMessage(content=language_detect_prompt)]]).generations[0][0].text.strip()
            )
            regex = r"\%([^%]+)\%"
            language = re.findall(regex, detected_language)[-1]

        except Exception as e:
            language = "English"
        return language
    
    def _format_dict_list(self, dict_list: list[dict]):
        result = ""
        for item in dict_list:
            for category, info in item.items():
                result += f"{category.capitalize().replace('_', ' ')}: \n"
                result += json.dumps(info, indent=4).replace("{", "<").replace("}", ">")
                result += "\n\n"
        return result
