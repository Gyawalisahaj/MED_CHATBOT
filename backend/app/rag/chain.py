from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from app.rag.retriever import get_medical_retriever
from app.core.config import settings
from app.core.prompts import MEDICAL_PROMPT, CONDENSE_PROMPT

_chain = None

def get_rag_chain():
    global _chain

    if _chain is None:
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE
        )

        retriever = get_medical_retriever()

        _chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": MEDICAL_PROMPT},
            condense_question_prompt=CONDENSE_PROMPT,
            return_source_documents=True
        )

    return _chain