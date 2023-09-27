import logging
from fastapi import HTTPException
from langchain import LLMChain
from langchain.callbacks import get_openai_callback
from langdetect import detect

from ai.schemas.schemas import QARequest
from ai.llm.base_model.langchain_openai import LangchainOpenAI
from ai.core.utils import preprocess_suggestion_request, check_hello
from config.constants import ErrorChatMessage
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory

async def chat(request: QARequest) -> str:
    processed_request = preprocess_suggestion_request(request)

    question=processed_request.get("question")
    language = processed_request.get("language")
    qa_chain =  LangchainOpenAI(
        question=question,
        metadata=processed_request.get("metadata"),
        language = language
    ).get_chain()

    try:
        with get_openai_callback() as cb:
            chat_history = processed_request.get("chat_history")
            if check_hello(question):
                chat_history = ""
            response = qa_chain({
                            "question": question,
                            "chat_history": chat_history,
                        })
            logging.info(f"Response: {response}")
            logging.info(
                f"[Tokens used: {cb.total_tokens} "
                f"(Prompt tokens: {cb.prompt_tokens}; "
                f"Completion tokens: {cb.completion_tokens})"
            )
            
    except Exception as e:
        logging.exception(e)
        lang = detect(question)
        answer = ErrorChatMessage.VI if lang == "vi" else ErrorChatMessage.EN
        return answer

    return response["answer"]


async def chat_without_docs(request: QARequest) -> str:
    processed_request = preprocess_suggestion_request(request)

    question=processed_request.get("question")
    language = processed_request.get("language")

    chat_history = processed_request.get("chat_history")

    chain = LangchainOpenAI(question=question, metadata=processed_request.get("metadata"),
        language = language, chat_history= chat_history)
    

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

