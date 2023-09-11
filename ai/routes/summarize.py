from ai.llm.base_model.langchain_openai import LangchainOpenAI

async def summarize(question: str) -> str:
    chain = LangchainOpenAI(question)
    response = chain.summarize_question(question)
    return response