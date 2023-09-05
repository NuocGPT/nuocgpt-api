import logging
from langchain.callbacks import get_openai_callback

from ai.schemas.schemas import QARequest
from ai.llm.base_model.langchain_openai import LangchainOpenAI
from ai.core.utils import preprocess_suggestion_request
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

async def chat(request: QARequest) -> str:
    # question = request.question
    # chain = LangchainOpenAI(question)
    # vectorstore = chain.vectorstore
    # qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0), chain_type="stuff", retriever=vectorstore.as_retriever(search_type="mmr"))
    # docs = chain.get_relevant_documents(question=question, chat_history=[question])
    # response = qa_chain.run(input_documents=docs, query=question)
    processed_request = preprocess_suggestion_request(request)

    language = processed_request.get("language")

    qa_chain =  LangchainOpenAI(
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
