import logging
import os
from typing import Any, Dict

from langchain import LLMChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from langdetect import detect

from ai.core.constants import IngestDataConstants
from ai.core.utils import check_goodbye, check_hello, preprocess_suggestion_request
from ai.llm.base_model.langchain_openai import LangchainOpenAI
from ai.llm.data_loader.load_langchain_config import LangChainDataLoader
from ai.schemas.schemas import QARequest
from config.constants import ErrorChatMessage


async def chat(request: QARequest) -> str:
    processed_request = preprocess_suggestion_request(request)

    question = processed_request.get("question")
    language = processed_request.get("language")

    if check_hello(question):
        chain = LLMChain(
            llm=LangchainOpenAI.load_llm_model()[2],
            prompt=LangChainDataLoader().prompts["helloPrompt"],
        )
        return chain.generate([{"message": question}]).generations[0][0].text.strip()

    if check_goodbye(question):
        chain = LLMChain(
            llm=LangchainOpenAI.load_llm_model()[2],
            prompt=LangChainDataLoader().prompts["goodbyePrompt"],
        )
        return chain.generate([{"message": question}]).generations[0][0].text.strip()

    chain = LangchainOpenAI(
        question=question, metadata=processed_request.get("metadata"), language=language
    )

    # sensor_lib_vts_folder_path = os.path.join(
    #     IngestDataConstants.TEMP_DB_FOLDER, "sensor_data_lib"
    # )
    # chain.sensor_lib_vts_retriever = chain.get_sensor_lib_retriever(
    #     sensor_lib_vts_folder_path
    # )

    # await chain.query_relevant_answers(question)

    # chain.data_loader.preprocessing_qa_prompt(
    #     metadata=chain._format_dict_list(chain.metadata or []),
    #     language=chain.lang,
    #     chat_history=chain.chat_history,
    #     relevant_answer=chain.relevant_answer if chain.relevant_answer != "" else None,
    # )

    try:
        with get_openai_callback() as cb:
            chat_history = processed_request.get("chat_history")
            # if chain.relevant_answer != "" and chain.score >= 0.8:
            #     output: Dict[str, Any] = {
            #         "answer": chain.relevant_answer,
            #         "score": chain.score,
            #     }
            #     if chain.output_parser:
            #         output.update(
            #             {"answer": chain.output_parser.parse(output["answer"])}
            #         )
            #     return output["answer"]

            qa_chain = chain.get_diamond_chain()
            result = qa_chain(
                {
                    "question": question,
                    "chat_history": chat_history,
                    "dataset": "diamond",
                }
            )
            if result["answer"] == "NO DATA":
                qa_chain = chain.get_chain()
                response = qa_chain(
                    {
                        "question": question,
                        "chat_history": chat_history,
                        "dataset": "normal",
                    }
                )
            else:
                return result["answer"]

    except Exception as e:
        logging.exception(e)
        lang = detect(question)
        answer = ErrorChatMessage.VI if lang == "vi" else ErrorChatMessage.EN
        return answer
    return response["answer"]


async def chat_without_docs(request: QARequest) -> str:
    processed_request = preprocess_suggestion_request(request)

    question = processed_request.get("question")
    language = processed_request.get("language")

    chat_history = processed_request.get("chat_history")

    if check_hello(question):
        chat_history = ""
        chain = LLMChain(
            llm=LangchainOpenAI.load_llm_model()[2],
            prompt=LangChainDataLoader().prompts["helloPrompt"],
        )
        return chain.generate([{"message": question}]).generations[0][0].text.strip()

    if check_goodbye(question):
        chain = LLMChain(
            llm=LangchainOpenAI.load_llm_model()[2],
            prompt=LangChainDataLoader().prompts["goodbyePrompt"],
        )
        return chain.generate([{"message": question}]).generations[0][0].text.strip()

    chain = LangchainOpenAI(
        question=question,
        metadata=processed_request.get("metadata"),
        language=language,
        chat_history=chat_history,
    )

    try:
        qa_prompt = chain.data_loader.prompts.get("qaWithoutDocsPrompt")

        memory = ConversationBufferMemory(memory_key="chat_history")

        llm_chain = LLMChain(
            llm=chain.llm_model,
            prompt=qa_prompt,
            verbose=True,
            memory=memory,
        )

        response = (
            llm_chain.generate([{"question": question}]).generations[0][0].text.strip()
        )
    except Exception as e:
        raise e
    return response
