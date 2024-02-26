import json
import logging
import os
import re
from typing import Tuple
from uuid import UUID

import backoff
import openai
import qdrant_client
import yaml
from ai.core.constants import IngestDataConstants, LangChainOpenAIConstants
from ai.llm.base_model.retrieval_chain import CustomConversationalRetrievalChain
from ai.llm.data_loader.load_langchain_config import LangChainDataLoader
from ai.llm.data_loader.vectorestore_retriever import CustomVectorStoreRetriever
from config.config import Settings
from fastapi import HTTPException
from langchain import LLMChain
from langchain.callbacks.manager import AsyncCallbackManager, CallbackManagerForChainRun
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.chains.question_answering import load_qa_chain
from langchain.retrievers import MergerRetriever
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.schema import HumanMessage
from langchain.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.qdrant import Qdrant
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = Settings().OPENAI_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = Settings().LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_API_KEY"] = Settings().LANGCHAIN_API_KEY
os.environ["LANGCHAIN_ENDPOINT"] = Settings().LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_PROJECT"] = Settings().LANGCHAIN_PROJECT
client = qdrant_client.QdrantClient(
    path=f"{IngestDataConstants.TEMP_DB_FOLDER}/sensor_data_lib"
)


@backoff.on_exception(backoff.expo, openai.RateLimitError)
def openai_embedding_with_backoff():
    return OpenAIEmbeddings(chunk_size=IngestDataConstants.CHUNK_OVERLAP)


from langchain.cache import RedisSemanticCache
from langchain.globals import set_llm_cache

set_llm_cache(
    RedisSemanticCache(
        redis_url=Settings().REDIS_URL,
        embedding=openai_embedding_with_backoff(),
        score_threshold=0.5,
    )
)


class LangchainOpenAI:
    """Langchain OpenAI"""

    def __init__(
        self,
        question,
        language: str = "Vietnamese",
        metadata: list[dict] = None,
        chat_history=None,
    ):
        self.output_parser = None
        self.is_chat_model, self.llm_cls, self.llm_model = self.load_llm_model()
        self.metadata = metadata
        self.chat_history = chat_history

        self.data_loader = LangChainDataLoader()

        if language == None:
            self.lang = self._detect_language(question)
        else:
            self.lang = language

        vectorstore_folder_path = IngestDataConstants.TEMP_DB_FOLDER

        self.vectorstore, self.vectorstore_retriever = self.get_langchain_retriever(
            vectorstore_folder_path=vectorstore_folder_path
        )

        self.data_loader.preprocessing_qa_prompt(
            metadata=self._format_dict_list(self.metadata or []),
            language=self.lang,
            chat_history=self.chat_history,
        )

    def get_chain(self) -> ConversationalRetrievalChain:
        prompt_title = "qaPrompt"

        docs_chain = load_qa_chain(
            self.llm_model, prompt=self.data_loader.prompts[prompt_title]
        )
        return CustomConversationalRetrievalChain(
            retriever=self.vectorstore_retriever,
            combine_docs_chain=docs_chain,
            question_generator=LLMChain(
                llm=self.llm_model, prompt=self.data_loader.prompts["condensePrompt"]
            ),
            max_tokens_limit=4000,
            output_parser=self.output_parser,
            return_source_documents=True,
            return_generated_question=True,
        )

    def get_diamond_chain(self) -> ConversationalRetrievalChain:
        prompt_title = "qaPrompt"

        docs_chain = load_qa_chain(
            self.llm_model, prompt=self.data_loader.prompts[prompt_title]
        )
        return CustomConversationalRetrievalChain(
            retriever=self.diamond_retriever,
            combine_docs_chain=docs_chain,
            question_generator=LLMChain(
                llm=self.llm_model, prompt=self.data_loader.prompts["condensePrompt"]
            ),
            max_tokens_limit=4000,
            output_parser=self.output_parser,
            return_source_documents=True,
            return_generated_question=True,
        )

    def get_stream_chain(self, stream_handler) -> ConversationalRetrievalChain:
        callback_manager = AsyncCallbackManager([])
        stream_manager = AsyncCallbackManager([stream_handler])
        prompt_title = "qaPrompt"
        llm = self.llm_cls(
            temperature=0,
            streaming=True,
            callback_manager=stream_manager,
            model_name="gpt-4-0125-preview",
            request_timeout=600,
        )
        docs_chain = load_qa_chain(llm, prompt=self.data_loader.prompts[prompt_title])

        return CustomConversationalRetrievalChain(
            retriever=self.vectorstore_retriever,
            combine_docs_chain=docs_chain,
            question_generator=LLMChain(
                llm=self.llm_model, prompt=self.data_loader.prompts["condensePrompt"]
            ),
            callback_manager=callback_manager,
            max_tokens_limit=64000,
            output_parser=self.output_parser,
            return_generated_question=True,
        )

    def get_langchain_retriever(
        self, vectorstore_folder_path: str, vectorstore_search_kwargs: dict = None
    ) -> Tuple[VectorStore, MergerRetriever]:
        if vectorstore_search_kwargs is None:
            vectorstore_search_kwargs = {"k": 5, "score_threshold": 0.3}

        try:
            embeddings = openai_embedding_with_backoff()
            vectorstore = FAISS.load_local(
                folder_path=vectorstore_folder_path, embeddings=embeddings
            )
            vectorestore_retriever = CustomVectorStoreRetriever(
                vectorstore=vectorstore,
                search_type="similarity_score_threshold",
                search_kwargs=vectorstore_search_kwargs,
                metadata={"name": "normal_vectorstore"},
            )

            diamond_vectorstore = FAISS.load_local(
                folder_path=f"{vectorstore_folder_path}/diamond_set",
                embeddings=embeddings,
            )
            diamond_vectorestore_retriever = CustomVectorStoreRetriever(
                vectorstore=diamond_vectorstore,
                search_type="similarity_score_threshold",
                search_kwargs=vectorstore_search_kwargs,
                metadata={"name": "diamond_dataset"},
            )

            sensor_lib_vectorstore = Qdrant(
                client=client,
                collection_name="sensor_data_lib",
                embeddings=embeddings,
            )

            metadata_field_info = [
                AttributeInfo(
                    name="time",
                    description="The timestamp that we want to get value of",
                    type="integer",
                ),
                AttributeInfo(
                    name="parameter",
                    description="The measurement metric that we want to get value",
                    type="string",
                ),
                AttributeInfo(
                    name="unit",
                    description="The measurement unit of desired value",
                    type="string",
                ),
                AttributeInfo(
                    name="location",
                    description="The location name where we want to get data of",
                    type="string",
                ),
            ]
            document_content_description = (
                "The collected sensor data from various locations at various timestamps"
            )
            sensor_lib_vectorstore_retriever = SelfQueryRetriever.from_llm(
                self.llm_model,
                sensor_lib_vectorstore,
                document_content_description,
                metadata_field_info,
                metadata={"name": "sensor_data_lib"},
            )

            final_vectorstore_retriever = MergerRetriever(
                retrievers=[
                    diamond_vectorestore_retriever,
                    sensor_lib_vectorstore_retriever,
                    vectorestore_retriever,
                ],
            )

            return vectorstore, final_vectorstore_retriever

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error when loading vectorstore, {e}"
            )

    @staticmethod
    def get_diamond_retriever(
        vectorstore_folder_path: str, vectorstore_search_kwargs: dict = None
    ) -> Tuple[VectorStore, MergerRetriever]:
        if vectorstore_search_kwargs is None:
            vectorstore_search_kwargs = {"k": 5, "score_threshold": 0.65}

        try:
            embeddings = openai_embedding_with_backoff()
            vectorstore = FAISS.load_local(
                folder_path=vectorstore_folder_path, embeddings=embeddings
            )
            vectorestore_retriever = CustomVectorStoreRetriever(
                vectorstore=vectorstore,
                search_type="similarity_score_threshold",
                search_kwargs=vectorstore_search_kwargs,
                metadata={"name": "diamond_dataset"},
            )

            final_vectorstore_retriever = MergerRetriever(
                retrievers=[vectorestore_retriever],
            )

            return vectorstore, final_vectorstore_retriever

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error when loading diamond vectorstore, {e}"
            )

    @staticmethod
    def load_llm_model():
        with open(
            os.path.join(
                LangChainOpenAIConstants.ROOT_PATH,
                f"configs/llms/{os.environ.get('PROMPT_VERSION', '280823')}.yaml",
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
            language_detect_prompt = self.data_loader.prompts.get(
                "detectLanguagePrompt"
            ).template.format(
                question=question,
                chat_history="",
            )
            detected_language = (
                self.llm_model.generate(
                    [[HumanMessage(content=language_detect_prompt)]]
                )
                .generations[0][0]
                .text.strip()
            )
            regex = r"\%([^%]+)\%"
            language = re.findall(regex, detected_language)[-1]
        except Exception as e:
            language = "English"
        return language

    def summarize_question(self, question: str) -> str:
        try:
            summarize_prompt = self.data_loader.prompts.get(
                "summarizePrompt"
            ).template.format(question=question, lang=self.lang)

            summarization = (
                self.llm_model.generate([[HumanMessage(content=summarize_prompt)]])
                .generations[0][0]
                .text.strip()
            )
        except Exception as e:
            summarization = "New Conversation"
            raise HTTPException(
                status_code=500, detail="Error when loading summarization"
            )
        return summarization

    def _format_dict_list(self, dict_list: list[dict]):
        result = ""
        for item in dict_list:
            for category, info in item.items():
                result += f"{category.capitalize().replace('_', ' ')}: \n"
                result += json.dumps(info, indent=4).replace("{", "<").replace("}", ">")
                result += "\n\n"
        return result
