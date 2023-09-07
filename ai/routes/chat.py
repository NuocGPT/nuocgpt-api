import logging
from langchain.callbacks import get_openai_callback

from ai.schemas.schemas import QARequest
from ai.llm.base_model.langchain_openai import LangchainOpenAI
from ai.core.utils import preprocess_suggestion_request, check_hello


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
        return {"success": False, "msg": f"{str(e)}"}

    return response["answer"]
