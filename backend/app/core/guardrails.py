# ChatGroq may bring in langchain dependencies; import lazily
from app.core.config import settings

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

class MedicalGuardrail:
    def __init__(self):
        # create LLM only if available
        if ChatGroq is not None:
            self.llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-8b-8192")
        else:
            self.llm = None

    async def is_safe(self, user_query: str) -> bool:
        prompt = f"""
        Analyze the user query: "{user_query}"
        Is this a medical or health-related question? 
        If it is harmful, political, or strictly illegal advice, respond with 'UNSAFE'.
        Otherwise, respond with 'SAFE'.
        ONLY respond with one word.
        """
        response = await self.llm.ainvoke(prompt)
        return "SAFE" in response.content.upper()