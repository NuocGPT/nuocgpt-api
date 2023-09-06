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
        question,
        language: str = None,
        metadata: list[dict] = None,
    ):
        self.output_parser = None
        self.is_chat_model, self.llm_cls, self.llm_model = self.load_llm_model()

        self.data_loader = LangChainDataLoader()

        if language == None:
            self.lang = self._detect_language(question)
        else:
            self.lang = language

        self.data_loader.preprocessing_qa_prompt(
            metadata=self._format_dict_list(metadata or []),
            language=self.lang
        )

        vectorstore_folder_path = os.path.join(IngestDataConstants.TEMP_DB_FOLDER, f"{self.lang}/")
        self.vectorstore, self.vectorstore_retriever = self.get_langchain_retriever(vectorstore_folder_path=vectorstore_folder_path)
        s3_client = AWSService()
        s3_client.download_from_s3(vectorstore_folder_path)

    def get_chain(self) -> CustomConversationalRetrievalChain:
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
    def get_langchain_retriever(vectorstore_folder_path: str, vectorstore_search_kwargs: dict = None) -> Tuple[VectorStore, MergerRetriever]:
        if vectorstore_search_kwargs is None:
            vectorstore_search_kwargs = {"k": 3, "score_threshold": 0.3}

        try:
            embeddings = openai_embedding_with_backoff()
            vectorstore = Chroma(persist_directory=vectorstore_folder_path, embedding_function=embeddings)
            
            return vectorstore, vectorstore.as_retriever()
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error when loading vectorstore")

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
    
    def get_document_sources(
        self, question: str, chat_history: list, relevant_threshold: float = 0.65, top_k: int = 4
    ) -> list:
        """Get document sources for question/answering."""
        doc_sources = set()

        search_result = self.get_relevant_documents(question, chat_history, top_k=top_k)

        for document, score in search_result[:top_k]:
            if score > relevant_threshold:
                source_url = document.metadata.get("source", None)
                doc_sources.add(source_url)

        return list(doc_sources)
    
    def get_relevant_documents(self, question: str, chat_history: list, top_k: int = 1) -> list:
        """Get document sources for question/answering."""
        chat_history_str = self._get_chat_history_str(chat_history)
        condense_question_prompt = self.data_loader.prompts["condensePrompt"].format(
            question=question,
            chat_history=chat_history_str,
        )
        condense_question = self.llm_model.generate([[HumanMessage(content=condense_question_prompt)]])
        if condense_question:
            condense_question = condense_question.generations[0][0].text.strip()

        search_result = self.vectorstore.similarity_search_with_relevance_scores(query=condense_question)

        return search_result[:top_k]
    
    def _get_chat_history_str(self, chat_history: list) -> str:
        buffer = ""
        for dialogue_turn in chat_history:
            customer = f"Customer: {dialogue_turn[0]}"
            ai = f"Agent: {dialogue_turn[1]}"
            buffer += "\n" + "\n".join([customer, ai])
        return buffer
    
    def _format_dict_list(self, dict_list: list[dict]):
        result = ""
        for item in dict_list:
            for category, info in item.items():
                result += f"{category.capitalize().replace('_', ' ')}: \n"
                result += json.dumps(info, indent=4).replace("{", "<").replace("}", ">")
                result += "\n\n"
        return result
