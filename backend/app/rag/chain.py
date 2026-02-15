from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.rag.retriever import get_medical_retriever
from app.core.config import settings
from app.core.prompts import MEDICAL_PROMPT

_chain = None


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain():
    global _chain

    if _chain is None:
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE
        )

        retriever = get_medical_retriever()

        prompt = ChatPromptTemplate.from_messages([
            ("system", MEDICAL_PROMPT),
            ("human", "{question}")
        ])

        _chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    return _chain