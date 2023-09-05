from ai.schemas.schemas import QARequest
from ai.llm.base_model.langchain_openai import LangchainOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

async def chat(request: QARequest) -> str:
    question = request.question

    chain = LangchainOpenAI(question)
    vectorstore = chain.vectorstore
    qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0), chain_type="stuff", retriever=vectorstore.as_retriever(search_type="mmr"))
    docs = chain.get_relevant_documents(question=question, chat_history=[question])
    response = qa_chain.run(input_documents=docs, query=question)

    return response
