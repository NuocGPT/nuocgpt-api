import logging
from langchain.callbacks import get_openai_callback

from schemas.schemas import QARequest
from llm.base_model.langchain_openai import LangchainOpenAI
from core.utils import preprocess_suggestion_request

async def chat(request: QARequest) -> str:
    processed_request = preprocess_suggestion_request(request)

    language = processed_request.get("language")

    qa_chain =  LangchainOpenAI(
        vectorstore=processed_request.get("vectorstore"),
        vectorstore_retriever= processed_request.get("vectorstore_retriever"),
        metadata=processed_request.get("metadata"),
        language = language
    ).get_chain()

    try:
        with get_openai_callback() as cb:
            chat_history = processed_request.get("chat_history")

            response = qa_chain({
                            "question": processed_request.get("question"),
                            "chat_history": chat_history,
                        })
            
    except Exception as e:
        logging.exception(e)
        return {"success": False, "msg": f"{str(e)}"}

    return response
