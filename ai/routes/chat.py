from schemas.schemas import QARequest
from llm.base_model.langchain_openai import LangchainOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from core.constants import IngestDataConstants
import openai
import backoff

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def openai_embedding_with_backoff():
    return OpenAIEmbeddings(chunk_size=IngestDataConstants.CHUNK_OVERLAP)

async def chat(request: QARequest) -> str:
    question = request.question

    chain = LangchainOpenAI(question)
    embeddings = openai_embedding_with_backoff()
    vectorstore = Chroma(persist_directory=chain.vectorstore, embedding_function=embeddings)
    qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0), chain_type="stuff", retriever=vectorstore.as_retriever(search_type="mmr"))
    response = qa_chain.run(question)

    return response